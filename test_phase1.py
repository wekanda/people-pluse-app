#!/usr/bin/env python3
"""
Phase 1 Endpoint Testing Script
Tests RBAC, Leave Management, and e-PFile endpoints
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8001"

# Test users
users = {
    "admin": {"email": "admin@peoplepluse.com", "password": "admin123"},
    "manager": {"email": "manager@peoplepluse.com", "password": "manager123"},
    "staff": {"email": "staff@peoplepluse.com", "password": "staff123"},
}

tokens = {}


def login_all_users():
    """Login all test users and get tokens."""
    print("\n=== Logging in Test Users ===")
    for role, creds in users.items():
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": creds["email"], "password": creds["password"]}
        )
        if response.status_code == 200:
            tokens[role] = response.json()["access_token"]
            print(f"✓ Logged in as {role}")
        else:
            print(f"✗ Failed to login {role}: {response.text}")
    return tokens


def test_leave_types():
    """Test GET /leave/types endpoint."""
    print("\n=== Testing Leave Types Endpoint ===")
    response = requests.get(
        f"{BASE_URL}/leave/types",
        headers={"Authorization": f"Bearer {tokens.get('admin')}"}
    )
    if response.status_code == 200:
        types = response.json()
        print(f"✓ Retrieved {len(types)} leave types:")
        for lt in types:
            print(f"  - {lt['name']}: {lt['annual_entitlement_days']} days")
    else:
        print(f"✗ Failed to get leave types: {response.text}")


def test_leave_balance():
    """Test GET /leave/balance endpoint."""
    print("\n=== Testing Leave Balance Endpoint ===")
    employee_id = 1
    response = requests.get(
        f"{BASE_URL}/leave/balance/{employee_id}",
        headers={"Authorization": f"Bearer {tokens.get('admin')}"}
    )
    if response.status_code == 200:
        balances = response.json()
        print(f"✓ Retrieved leave balances for employee {employee_id}:")
        for bal in balances[:3]:  # Show first 3
            print(f"  - Leave Type {bal['leave_type_id']}: {bal['balance']} days available")
    else:
        print(f"✗ Failed to get leave balance: {response.text}")


def test_leave_request():
    """Test POST /leave/request endpoint."""
    print("\n=== Testing Leave Request Endpoint ===")
    
    payload = {
        "employee_id": 1,
        "leave_type_id": 1,  # Annual Leave
        "start_date": str(date.today() + timedelta(days=5)),
        "end_date": str(date.today() + timedelta(days=7)),
        "reason": "Vacation"
    }
    
    response = requests.post(
        f"{BASE_URL}/leave/request",
        json=payload,
        headers={"Authorization": f"Bearer {tokens.get('admin')}"}
    )
    
    if response.status_code == 200:
        leave_request = response.json()
        print(f"✓ Created leave request ID {leave_request['id']}")
        print(f"  - Employee: {leave_request['employee_id']}")
        print(f"  - Days: {leave_request['days']}")
        print(f"  - Status: {leave_request['status']}")
        return leave_request['id']
    else:
        print(f"✗ Failed to create leave request: {response.text}")
        return None


def test_pending_approvals():
    """Test GET /leave/pending endpoint."""
    print("\n=== Testing Pending Approvals Endpoint ===")
    response = requests.get(
        f"{BASE_URL}/leave/pending",
        headers={"Authorization": f"Bearer {tokens.get('manager')}"}
    )
    if response.status_code == 200:
        requests_list = response.json()
        print(f"✓ Retrieved {len(requests_list)} pending approvals")
        for req in requests_list[:3]:  # Show first 3
            print(f"  - Request {req['id']}: Employee {req['employee_id']}, {req['days']} days")
    else:
        print(f"✗ Failed to get pending approvals: {response.text}")


def test_document_types():
    """Test GET /document-types/all endpoint."""
    print("\n=== Testing Document Types Endpoint ===")
    response = requests.get(
        f"{BASE_URL}/employees/document-types/all",
        headers={"Authorization": f"Bearer {tokens.get('admin')}"}
    )
    if response.status_code == 200:
        types = response.json()
        print(f"✓ Retrieved {len(types)} document types:")
        categories = {}
        for dt in types:
            cat = dt['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(dt['name'])
        
        for cat, names in categories.items():
            print(f"  {cat}: {len(names)} types")
    else:
        print(f"✗ Failed to get document types: {response.text}")


def test_file_summary():
    """Test GET /employees/{employee_id}/file-summary endpoint."""
    print("\n=== Testing e-PFile Summary Endpoint ===")
    employee_id = 1
    response = requests.get(
        f"{BASE_URL}/employees/{employee_id}/file-summary",
        headers={"Authorization": f"Bearer {tokens.get('admin')}"}
    )
    if response.status_code == 200:
        summary = response.json()
        print(f"✓ Retrieved e-PFile summary for employee {employee_id}:")
        print(f"  - Required Documents: {summary['total_required_documents']}")
        print(f"  - Uploaded: {summary['uploaded_documents']}")
        print(f"  - Approved: {summary['approved_documents']}")
        print(f"  - Completeness: {summary['completeness_percentage']}%")
        if summary['missing_required_documents']:
            print(f"  - Missing: {', '.join(summary['missing_required_documents'][:3])}")
    else:
        print(f"✗ Failed to get file summary: {response.text}")


def test_rbac_denied():
    """Test RBAC - staff accessing manager endpoint should be denied."""
    print("\n=== Testing RBAC Access Control ===")
    response = requests.get(
        f"{BASE_URL}/leave/pending",
        headers={"Authorization": f"Bearer {tokens.get('staff')}"}
    )
    if response.status_code == 403:
        print("✓ Staff correctly denied access to manager endpoint (403)")
    else:
        print(f"✗ RBAC check failed: expected 403, got {response.status_code}")


def main():
    """Run all Phase 1 tests."""
    print("=" * 60)
    print("Phase 1: RBAC, Leave Management, e-PFile Testing")
    print("=" * 60)
    
    # Login
    login_all_users()
    if not tokens:
        print("❌ Failed to authenticate. Cannot run tests.")
        return
    
    # Run tests
    test_leave_types()
    test_leave_balance()
    leave_id = test_leave_request()
    test_pending_approvals()
    test_document_types()
    test_file_summary()
    test_rbac_denied()
    
    print("\n" + "=" * 60)
    print("✓ Phase 1 Testing Complete!")
    print("=" * 60)
    print("\nPhase 1 Features Implemented:")
    print("  1. Role-Based Access Control (RBAC)")
    print("     - hr_admin: Full access")
    print("     - project_manager: Team access")
    print("     - staff: Own data only")
    print("\n  2. Leave Management")
    print("     - 8 leave types (Ugandan standards)")
    print("     - Leave balance tracking")
    print("     - Request → Approval → Balance Update workflow")
    print("     - Manager approval for leave requests")
    print("\n  3. e-PFile (Electronic Personnel File)")
    print("     - 19 document types")
    print("     - Document upload with approval")
    print("     - Completeness tracking")
    print("     - Expiry date monitoring")
    print("\nEndpoints Available:")
    print("  - GET /leave/types")
    print("  - GET /leave/balance/{employee_id}")
    print("  - POST /leave/request")
    print("  - POST /leave/request/{request_id}/approve")
    print("  - GET /leave/pending")
    print("  - POST /employees/{employee_id}/documents")
    print("  - GET /employees/{employee_id}/file-summary")
    print("  - GET /employees/document-types/all")


if __name__ == "__main__":
    main()
