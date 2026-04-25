#!/usr/bin/env python3
"""
Distributive - AI and Cloud Project
Streamlit application with MongoDB integration
"""

import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from datetime import datetime
import json
from typing import Optional, List, Dict
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'distributive_db')

# Page configuration
st.set_page_config(
    page_title="Distributive - AI & Cloud",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MONGODB CONNECTION
# ============================================================================

@st.cache_resource
def get_mongo_client():
    """Get MongoDB client with retry logic."""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            # Test the connection
            client.admin.command('ping')
            st.success("✅ MongoDB connected successfully!")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2 ** (retry_count - 1))  # Exponential backoff
            else:
                st.warning(f"⚠️ MongoDB unavailable (attempt {retry_count}/{max_retries}): {str(e)}")
                return None
        except Exception as e:
            st.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
            return None
    
    return None

def get_database(client: Optional[MongoClient]):
    """Get database instance."""
    if client is None:
        return None
    try:
        return client[MONGO_DB_NAME]
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        return None

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def insert_document(collection_name: str, document: Dict):
    """Insert a document into a collection."""
    try:
        client = get_mongo_client()
        if client is None:
            st.error("Cannot connect to MongoDB")
            return None
        
        db = get_database(client)
        if db is None:
            st.error("Cannot access database")
            return None
        
        collection = db[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id
    except Exception as e:
        st.error(f"Error inserting document: {str(e)}")
        return None

def get_documents(collection_name: str, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
    """Retrieve documents from a collection."""
    try:
        client = get_mongo_client()
        if client is None:
            st.error("Cannot connect to MongoDB")
            return []
        
        db = get_database(client)
        if db is None:
            st.error("Cannot access database")
            return []
        
        collection = db[collection_name]
        filter_dict = filter_dict or {}
        documents = list(collection.find(filter_dict).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        
        return documents
    except Exception as e:
        st.error(f"Error retrieving documents: {str(e)}")
        return []

def delete_document(collection_name: str, document_id: str):
    """Delete a document from a collection."""
    try:
        from bson import ObjectId
        client = get_mongo_client()
        if client is None:
            st.error("Cannot connect to MongoDB")
            return False
        
        db = get_database(client)
        if db is None:
            st.error("Cannot access database")
            return False
        
        collection = db[collection_name]
        result = collection.delete_one({'_id': ObjectId(document_id)})
        return result.deleted_count > 0
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False

# ============================================================================
# UI COMPONENTS
# ============================================================================

def header():
    """Display application header."""
    st.title("☁️ Distributive - AI & Cloud")
    st.markdown(
        """A comprehensive platform for distributed computing, 
        AI model deployment, and cloud infrastructure management."""
    )
    st.divider()

def health_check():
    """Display health check status."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Status")
        client = get_mongo_client()
        if client:
            try:
                client.admin.command('ping')
                st.success("✅ All systems operational")
                st.info(f"📦 MongoDB: Connected to {MONGO_DB_NAME}")
            except Exception as e:
                st.error(f"❌ System error: {str(e)}")
        else:
            st.warning("⚠️ MongoDB unavailable - some features disabled")
    
    with col2:
        st.subheader("Environment")
        st.text(f"URI: {MONGO_URI}")
        st.text(f"Database: {MONGO_DB_NAME}")
        st.text(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def demo_section():
    """Display demo section for database operations."""
    st.header("📊 Data Management Demo")
    
    with st.expander("📝 Add New Entry", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Project Name")
        with col2:
            category = st.selectbox("Category", ["AI", "Cloud", "DevOps", "Data"])
        
        description = st.text_area("Description")
        
        if st.button("➕ Add Entry", use_container_width=True):
            if name and description:
                document = {
                    "name": name,
                    "category": category,
                    "description": description,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                result = insert_document("projects", document)
                if result:
                    st.success(f"✅ Entry added with ID: {result}")
                    st.rerun()
            else:
                st.error("Please fill all fields")
    
    with st.expander("📚 View All Entries"):
        documents = get_documents("projects")
        
        if documents:
            st.success(f"Found {len(documents)} entries")
            
            for i, doc in enumerate(documents):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                    
                    with col1:
                        st.subheader(f"{doc.get('name', 'Unnamed')}")
                        st.write(f"**Category:** {doc.get('category', 'N/A')}")
                        st.write(f"**Description:** {doc.get('description', '')}")
                        if 'created_at' in doc:
                            st.caption(f"Created: {doc['created_at']}")
                    
                    with col2:
                        st.text(f"ID: {doc['_id'][:8]}...")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_{i}"):
                            if delete_document("projects", doc['_id']):
                                st.success("Entry deleted")
                                st.rerun()
        else:
            st.info("No entries yet. Add one above!")

def info_section():
    """Display information section."""
    st.header("ℹ️ About This Application")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Technology Stack")
        st.markdown("""
        - **Frontend:** Streamlit
        - **Backend:** Python
        - **Database:** MongoDB
        - **Deployment:** Docker + Kubernetes
        - **Orchestration:** Minikube (local)
        """)
    
    with col2:
        st.subheader("📈 Features")
        st.markdown("""
        - ✅ MongoDB integration
        - ✅ CRUD operations
        - ✅ Health monitoring
        - ✅ Containerized
        - ✅ Kubernetes-ready
        """)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    header()
    
    # Initialize MongoDB connection
    client = get_mongo_client()
    
    # Navigation
    page = st.sidebar.radio(
        "📍 Navigation",
        ["Dashboard", "Data Manager", "About"]
    )
    
    if page == "Dashboard":
        health_check()
    elif page == "Data Manager":
        demo_section()
    elif page == "About":
        info_section()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 12px;'>
            Distributive v1.0 | Powered by Streamlit & MongoDB<br>
            🔗 Database: {}<br>
            ⏰ Last Updated: {}
        </div>
        """.format(
            MONGO_DB_NAME,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
