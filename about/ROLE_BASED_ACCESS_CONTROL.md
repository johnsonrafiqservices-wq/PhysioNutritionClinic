# Role-Based Access Control (RBAC) Implementation

## Overview
The PhysioNutrition Clinic System now implements comprehensive role-based access control to ensure users can only access data and functions appropriate to their role.

## Security Layers

### 1. **Middleware Protection** (Global Level)
- `RoleBasedAccessMiddleware`: Checks every request against user permissions
- `DataAccessControlMiddleware`: Prevents unauthorized data access attempts
- Automatically redirects unauthorized users to dashboard with error messages

### 2. **View Decorators** (Function Level)
- `@app_access_required('app_name')`: Ensures user can access the app
- `@permission_required('app_name', 'action')`: Checks specific permissions
- `@medical_staff_required`: Restricts to clinical staff only
- `@lab_staff_required`: Laboratory staff only
- `@pharmacy_staff_required`: Pharmacy staff only
- `@finance_staff_required`: Billing/finance staff only
- `@admin_or_manager_required`: Management level only

### 3. **Template Tags** (UI Level)
- `{% if user|has_app:'patients' %}`: Show/hide UI elements
- `{% if user|can:'billing:create' %}`: Check specific permissions
- Dynamic sidebar based on user role

## Role Permissions Matrix

### Administrative Roles
| Role | Apps Access | Permissions |
|------|------------|-------------|
| **System Administrator** | All modules | Full CRUD + Admin |
| **Clinic Manager** | All except admin panel | Full CRUD |
| **Medical Director** | Clinical modules | Full CRUD |

### Clinical Staff
| Role | Primary Access | Limited Access |
|------|---------------|----------------|
| **Doctor** | Patients, Appointments, Medical Records, Lab, Pharmacy | Read-only: Billing, Reports |
| **Physiotherapist** | Patients, Appointments, Medical Records | Read-only: Lab, Billing |
| **Nutritionist** | Patients, Appointments, Medical Records | Read-only: Lab, Billing |
| **Nurse** | Patients, Appointments, Medical Records | Read-only: Lab |
| **Clinical Assistant** | Patients, Appointments | Read-only: Medical Records |

### Department Staff
| Role | Primary Access | Limited Access |
|------|---------------|----------------|
| **Lab Technician** | Laboratory | Read-only: Patients |
| **Lab Manager** | Laboratory | Read-only: Patients, Reports |
| **Pharmacist** | Pharmacy | Read-only: Patients, Appointments |
| **Billing Officer** | Billing | Read-only: Patients, Appointments |
| **Medical Records Officer** | Medical Records | Read-only: Patients |

### Support Roles
| Role | Primary Access | Limited Access |
|------|---------------|----------------|
| **Receptionist** | Patients, Appointments | Limited: Billing (create), Medical Records (read) |
| **HR Manager** | Staff Management | Read-only: Budget, Reports |
| **IT Support** | Read all modules | Update: Settings, Accounts |

## Security Features

### 1. **URL Protection**
- All URLs are protected by namespace checking
- Direct object access is prevented
- Unauthorized access attempts are logged

### 2. **Data Filtering**
- Users only see data relevant to their department
- Patient data access is controlled by role
- Financial data restricted to authorized staff

### 3. **Action-Based Permissions**
Each role has specific permissions:
- **Create**: Add new records
- **Read**: View existing records
- **Update**: Modify records
- **Delete**: Remove records
- **Admin**: Administrative functions

### 4. **Audit Trail**
- All access attempts are monitored
- Failed access attempts trigger warnings
- User actions are logged for compliance

## Implementation Status

### ✅ Completed
- Patient module access control
- Laboratory module restrictions
- Pharmacy module protection
- Billing access control
- Template-based UI filtering
- Middleware enforcement
- Permission decorators

### 🔧 Active Protection
- All views require authentication
- Role-based sidebar navigation
- Department-specific data access
- CRUD operation restrictions

## Testing Access Control

### Test Scenarios
1. **Receptionist** → Cannot access Laboratory module
2. **Lab Technician** → Cannot edit patient records
3. **Pharmacist** → Cannot access billing details
4. **Doctor** → Can view but not edit billing
5. **Admin** → Full access to all modules

### Verification Steps
1. Login as different roles
2. Try accessing restricted URLs directly
3. Verify sidebar shows only permitted modules
4. Check CRUD operations match role permissions
5. Confirm error messages for unauthorized access

## Security Best Practices

### For Administrators
1. Assign minimal necessary permissions
2. Review role assignments regularly
3. Monitor access logs for anomalies
4. Update permissions as responsibilities change

### For Developers
1. Always use permission decorators on views
2. Check permissions in templates
3. Never hardcode role checks
4. Use the centralized permission system

### For Users
1. Report any unexpected access
2. Don't share login credentials
3. Log out when not in use
4. Report suspicious activities

## Error Messages

Users will see appropriate messages when access is denied:

- "You do not have permission to access [Module Name]"
- "Your role ([Role Name]) does not have access to this module"
- "You do not have permission to [create/edit/delete] in [Module Name]"
- "This function is only available to [staff type]"
- "This function requires administrative privileges"

## Compliance

This RBAC system helps ensure:
- **HIPAA Compliance**: Patient data protection
- **Data Privacy**: Role-appropriate access
- **Audit Requirements**: Access logging
- **Principle of Least Privilege**: Minimal necessary access

## Support

For permission issues or role changes:
1. Contact system administrator
2. Provide current role and required access
3. Justify business need for access
4. Wait for approval and implementation

---

**Last Updated**: November 2024
**Version**: 1.0
**Status**: Active Protection Enabled
