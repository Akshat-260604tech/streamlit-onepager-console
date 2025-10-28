import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from supabase import create_client, Client
from pydantic import BaseModel

logger = logging.getLogger("DatabaseService")


class OnePagerRecord(BaseModel):
    """Pydantic model for one-pager database records"""
    id: Optional[int] = None
    request_id: str  # Unique identifier for each request
    session_id: Optional[str] = None  # Optional session identifier
    company_name: str
    website_url: str
    status: str  # 'in-progress', 'success', 'partial-success', 'error'
    generated_at: str  # ISO timestamp
    duration_ms: int
    folder_title: str
    base_path: str
    container: str
    pptx_filename: str
    pptx_blob_url: Optional[str] = None
    pptx_blob_path: Optional[str] = None
    metadata_blob_url: Optional[str] = None
    excel_provided: bool = False
    excel_filename: Optional[str] = None
    excel_size: Optional[int] = None
    excel_blob_url: Optional[str] = None
    excel_blob_path: Optional[str] = None
    excel_blob_info: Optional[Dict[str, Any]] = None  # Store Excel blob info as JSON
    sections_status: Optional[Dict[str, Any]] = None
    sections_response: Optional[Dict[str, Any]] = None
    section_sources: Optional[Dict[str, Any]] = None
    product_images: Optional[List[str]] = None
    products: Optional[List[Dict[str, Any]]] = None
    company_logo: Optional[str] = None
    azure_upload_ok: bool = False
    azure_upload_error: Optional[str] = None
    warnings: Optional[List[str]] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DatabaseService:
    """Service for managing one-pager records in Supabase database"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase credentials not found in environment variables")
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Database service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise ValueError(f"Failed to connect to Supabase: {str(e)}")

    def _prepare_record_for_db(self, record_data: OnePagerRecord) -> dict:
        """Prepare record data for database storage"""
        data = record_data.model_dump(exclude={'id', 'created_at', 'updated_at'})
        
        # Store Excel blob info in a dedicated JSON field
        excel_blob_url = data.pop('excel_blob_url', None)
        excel_blob_path = data.pop('excel_blob_path', None)
        
        if excel_blob_url or excel_blob_path:
            data['excel_blob_info'] = {
                'excel_blob_url': excel_blob_url,
                'excel_blob_path': excel_blob_path
            }
        else:
            data['excel_blob_info'] = None
            
        return data

    def _extract_record_from_db(self, db_record: dict) -> OnePagerRecord:
        """Extract record from database and populate Excel blob fields"""
        # Extract Excel blob fields from excel_blob_info if they exist
        if db_record.get('excel_blob_info') and isinstance(db_record['excel_blob_info'], dict):
            db_record['excel_blob_url'] = db_record['excel_blob_info'].get('excel_blob_url')
            db_record['excel_blob_path'] = db_record['excel_blob_info'].get('excel_blob_path')
        else:
            db_record['excel_blob_url'] = None
            db_record['excel_blob_path'] = None
            
        return OnePagerRecord(**db_record)

    async def create_one_pager_record(self, record_data: OnePagerRecord) -> Optional[OnePagerRecord]:
        """Create a new one-pager record in the database"""
        try:
            data = self._prepare_record_for_db(record_data)
            
            # Add current timestamp
            now = datetime.utcnow().isoformat()
            data['created_at'] = now
            data['updated_at'] = now

            result = self.client.table('one_pager_reports').insert(data).execute()

            if result.data and len(result.data) > 0:
                created_record = self._extract_record_from_db(result.data[0])
                logger.info(f"Created one-pager record with ID: {created_record.id}")
                return created_record
            else:
                logger.error("Failed to create one-pager record: No data returned")
                return None

        except Exception as e:
            logger.error(f"Error creating one-pager record: {str(e)}")
            return None

    async def update_one_pager_record(self, record_id: int, update_data: Dict[str, Any]) -> Optional[OnePagerRecord]:
        """Update an existing one-pager record"""
        try:
            # Handle Excel blob fields
            excel_blob_url = update_data.pop('excel_blob_url', None)
            excel_blob_path = update_data.pop('excel_blob_path', None)
            
            if excel_blob_url or excel_blob_path:
                update_data['excel_blob_info'] = {
                    'excel_blob_url': excel_blob_url,
                    'excel_blob_path': excel_blob_path
                }
            else:
                update_data['excel_blob_info'] = None

            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()

            result = self.client.table('one_pager_reports').update(update_data).eq('id', record_id).execute()

            if result.data and len(result.data) > 0:
                updated_record = self._extract_record_from_db(result.data[0])
                logger.info(f"Updated one-pager record with ID: {record_id}")
                return updated_record
            else:
                logger.error(f"Failed to update one-pager record with ID: {record_id}")
                return None

        except Exception as e:
            logger.error(f"Error updating one-pager record {record_id}: {str(e)}")
            return None

    async def get_one_pager_record(self, record_id: int) -> Optional[OnePagerRecord]:
        """Get a one-pager record by ID"""
        try:
            result = self.client.table('one_pager_reports').select('*').eq('id', record_id).execute()

            if result.data and len(result.data) > 0:
                return self._extract_record_from_db(result.data[0])
            else:
                logger.warning(f"One-pager record with ID {record_id} not found")
                return None

        except Exception as e:
            logger.error(f"Error getting one-pager record {record_id}: {str(e)}")
            return None

    async def get_one_pager_records_by_company(self, company_name: str) -> List[OnePagerRecord]:
        """Get all one-pager records for a specific company"""
        try:
            result = self.client.table('one_pager_reports').select('*').eq('company_name', company_name).order('created_at', desc=True).execute()

            records = [self._extract_record_from_db(record) for record in result.data]
            logger.info(f"Found {len(records)} records for company: {company_name}")
            return records

        except Exception as e:
            logger.error(f"Error getting records for company {company_name}: {str(e)}")
            return []

    async def get_recent_one_pager_records(self, limit: int = 100) -> List[OnePagerRecord]:
        """Get recent one-pager records"""
        try:
            result = self.client.table('one_pager_reports').select('*').order('created_at', desc=True).limit(limit).execute()

            records = [self._extract_record_from_db(record) for record in result.data]
            logger.info(f"Retrieved {len(records)} recent records")
            return records

        except Exception as e:
            logger.error(f"Error getting recent records: {str(e)}")
            return []

    async def get_one_pager_record_by_request_id(self, request_id: str) -> Optional[OnePagerRecord]:
        """Get a one-pager record by request ID"""
        try:
            result = self.client.table('one_pager_reports').select('*').eq('request_id', request_id).execute()

            if result.data and len(result.data) > 0:
                return self._extract_record_from_db(result.data[0])
            else:
                logger.warning(f"One-pager record with request_id {request_id} not found")
                return None

        except Exception as e:
            logger.error(f"Error getting one-pager record by request_id {request_id}: {str(e)}")
            return None

    async def get_in_progress_records_by_company(self, company_name: str) -> List[OnePagerRecord]:
        """Get all in-progress one-pager records for a specific company"""
        try:
            result = self.client.table('one_pager_reports').select('*').eq('company_name', company_name).eq('status', 'in-progress').order('created_at', desc=True).execute()

            records = [self._extract_record_from_db(record) for record in result.data]
            logger.info(f"Found {len(records)} in-progress records for company: {company_name}")
            return records

        except Exception as e:
            logger.error(f"Error getting in-progress records for company {company_name}: {str(e)}")
            return []

    async def get_recent_request_by_company(self, company_name: str) -> Optional[OnePagerRecord]:
        """Get the most recent one-pager record for a specific company"""
        try:
            result = self.client.table('one_pager_reports').select('*').eq('company_name', company_name).order('created_at', desc=True).limit(1).execute()

            if result.data and len(result.data) > 0:
                record = self._extract_record_from_db(result.data[0])
                logger.info(f"Found recent request for {company_name}: {record.request_id} (status: {record.status})")
                return record
            else:
                logger.info(f"No recent request found for company: {company_name}")
                return None

        except Exception as e:
            logger.error(f"Error getting recent request for company {company_name}: {str(e)}")
            return None

    async def update_one_pager_record_atomic(self, record_id: int, update_data: Dict[str, Any], expected_status: Optional[str] = None) -> Optional[OnePagerRecord]:
        """Atomically update a one-pager record with optional status check"""
        try:
            # Handle Excel blob fields
            excel_blob_url = update_data.pop('excel_blob_url', None)
            excel_blob_path = update_data.pop('excel_blob_path', None)
            
            if excel_blob_url or excel_blob_path:
                update_data['excel_blob_info'] = {
                    'excel_blob_url': excel_blob_url,
                    'excel_blob_path': excel_blob_path
                }
            else:
                update_data['excel_blob_info'] = None

            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()

            # Build the query
            query = self.client.table('one_pager_reports').update(update_data).eq('id', record_id)
            
            # Add status check if provided
            if expected_status is not None:
                query = query.eq('status', expected_status)

            result = query.execute()

            if result.data and len(result.data) > 0:
                updated_record = self._extract_record_from_db(result.data[0])
                logger.info(f"Atomically updated one-pager record with ID: {record_id}")
                return updated_record
            else:
                if expected_status:
                    logger.warning(f"Failed to atomically update record {record_id}: status mismatch or record not found")
                else:
                    logger.error(f"Failed to atomically update one-pager record with ID: {record_id}")
                return None

        except Exception as e:
            logger.error(f"Error atomically updating one-pager record {record_id}: {str(e)}")
            return None

    async def delete_one_pager_record(self, record_id: int) -> bool:
        """Delete a one-pager record"""
        try:
            result = self.client.table('one_pager_reports').delete().eq('id', record_id).execute()
            
            if result.data:
                logger.info(f"Deleted one-pager record with ID: {record_id}")
                return True
            else:
                logger.warning(f"One-pager record with ID {record_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting one-pager record {record_id}: {str(e)}")
            return False
