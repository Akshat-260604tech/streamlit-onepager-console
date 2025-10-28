#!/usr/bin/env python3
"""
Test script to verify Excel blob fields are being saved correctly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.database_service import DatabaseService, OnePagerRecord

async def test_excel_blob_save():
    """Test saving and retrieving Excel blob data"""
    print("🧪 Testing Excel blob field saving...")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        print("✅ Database service initialized")
        
        # Create a test record with Excel blob data
        test_record = OnePagerRecord(
            request_id=f"test_excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            company_name="Test Company Excel",
            website_url="https://testcompany.com",
            status="success",
            generated_at=datetime.now().isoformat(),
            duration_ms=15000,
            folder_title="test_excel_folder",
            base_path="one-pagers/test_excel",
            container="bynd-dev",
            pptx_filename="test.pptx",
            pptx_blob_url="https://example.com/test.pptx",
            pptx_blob_path="one-pagers/test_excel/test.pptx",
            metadata_blob_url="https://example.com/test_metadata.json",
            excel_provided=True,
            excel_filename="test_data.xlsx",
            excel_size=50000,
            excel_blob_url="https://example.com/test_data.xlsx",  # This should be saved
            excel_blob_path="one-pagers/test_excel/excel/test_data.xlsx",  # This should be saved
            sections_status={"about": {"ok": True}},
            sections_response={"about": "Test response"},
            section_sources={"about": ["https://testcompany.com/about"]},
            product_images=["https://example.com/product1.jpg"],
            products=[{"name": "Test Product", "price": "$99"}],
            company_logo="https://example.com/logo.png",
            azure_upload_ok=True,
            azure_upload_error=None,
            warnings=["Test warning"],
            error_type=None,
            error_message=None
        )
        
        print("📝 Created test record with Excel blob data:")
        print(f"   - Excel Blob URL: {test_record.excel_blob_url}")
        print(f"   - Excel Blob Path: {test_record.excel_blob_path}")
        
        # Save the record
        print("\n💾 Saving record to database...")
        saved_record = await db_service.create_one_pager_record(test_record)
        
        if saved_record:
            print("✅ Record saved successfully!")
            print(f"   - Record ID: {saved_record.id}")
            print(f"   - Excel Blob URL: {saved_record.excel_blob_url}")
            print(f"   - Excel Blob Path: {saved_record.excel_blob_path}")
            
            # Test retrieving the record
            print("\n🔍 Retrieving record from database...")
            retrieved_record = await db_service.get_one_pager_record(saved_record.id)
            
            if retrieved_record:
                print("✅ Record retrieved successfully!")
                print(f"   - Excel Blob URL: {retrieved_record.excel_blob_url}")
                print(f"   - Excel Blob Path: {retrieved_record.excel_blob_path}")
                
                # Verify the data matches
                if (retrieved_record.excel_blob_url == test_record.excel_blob_url and 
                    retrieved_record.excel_blob_path == test_record.excel_blob_path):
                    print("🎉 SUCCESS: Excel blob fields are being saved and retrieved correctly!")
                else:
                    print("❌ FAILURE: Excel blob fields don't match!")
                    print(f"   Expected URL: {test_record.excel_blob_url}")
                    print(f"   Retrieved URL: {retrieved_record.excel_blob_url}")
                    print(f"   Expected Path: {test_record.excel_blob_path}")
                    print(f"   Retrieved Path: {retrieved_record.excel_blob_path}")
            else:
                print("❌ Failed to retrieve record")
        else:
            print("❌ Failed to save record")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_excel_blob_update():
    """Test updating Excel blob data"""
    print("\n🔄 Testing Excel blob field updates...")
    
    try:
        db_service = DatabaseService()
        
        # Get a recent record to update
        recent_records = await db_service.get_recent_one_pager_records(1)
        
        if recent_records:
            record = recent_records[0]
            print(f"📝 Updating record ID: {record.id}")
            
            # Update with new Excel blob data
            update_data = {
                'excel_blob_url': f"https://updated-example.com/updated_{record.id}.xlsx",
                'excel_blob_path': f"one-pagers/updated_{record.id}/excel/updated_data.xlsx",
                'status': 'success'
            }
            
            print(f"   - New Excel Blob URL: {update_data['excel_blob_url']}")
            print(f"   - New Excel Blob Path: {update_data['excel_blob_path']}")
            
            # Update the record
            updated_record = await db_service.update_one_pager_record(record.id, update_data)
            
            if updated_record:
                print("✅ Record updated successfully!")
                print(f"   - Excel Blob URL: {updated_record.excel_blob_url}")
                print(f"   - Excel Blob Path: {updated_record.excel_blob_path}")
                
                if (updated_record.excel_blob_url == update_data['excel_blob_url'] and 
                    updated_record.excel_blob_path == update_data['excel_blob_path']):
                    print("🎉 SUCCESS: Excel blob fields are being updated correctly!")
                else:
                    print("❌ FAILURE: Excel blob fields not updated correctly!")
            else:
                print("❌ Failed to update record")
        else:
            print("⚠️ No records found to update")
            
    except Exception as e:
        print(f"❌ Error during update test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Excel blob field tests...")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_excel_blob_save())
    asyncio.run(test_excel_blob_update())
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
