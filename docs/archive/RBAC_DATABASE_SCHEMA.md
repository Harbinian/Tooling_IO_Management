# RBAC Database Schema
Tooling IO Management System

---

# 1 Overview

This document defines the RBAC database schema used by the Tooling IO Management System.

The RBAC schema supports:

- user authentication
- role assignment
- permission management
- organization hierarchy
- data scope control

The schema is designed for SQL Server and focuses on:

- simple initial deployment
- compatibility with existing systems
- scalability for enterprise integration

---

# 2 Table Overview

The RBAC system consists of the following tables.

Core identity tables

- sys_user
- sys_org

Authorization tables

- sys_role
- sys_permission

Relationship tables

- sys_user_role_rel
- sys_role_permission_rel
- sys_role_data_scope_rel

Optional future tables

- sys_login_log
- sys_user_org_rel

---

# 3 Table Naming Convention

All RBAC tables use the prefix:

sys_

Examples

sys_user  
sys_org  
sys_role  
sys_permission  

This prevents conflicts with business tables and keeps system tables organized.

---

# 4 User Table

Table Name

sys_user

Purpose

Stores system login users.

Each record represents a system identity.

Fields

id  
Primary key

user_id  
System user identifier

login_name  
Login username

display_name  
User display name

password_hash  
Password hash

mobile  
Mobile phone

email  
Email address

status  
active / disabled / locked

default_org_id  
Default organization

last_login_at  
Last login time

remark  
Remarks

created_at  
Created time

created_by  
Created by

updated_at  
Updated time

updated_by  
Updated by

SQL Example

    CREATE TABLE sys_user (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        user_id NVARCHAR(64) NOT NULL,
        login_name NVARCHAR(100) NOT NULL,
        display_name NVARCHAR(100) NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        mobile NVARCHAR(50) NULL,
        email NVARCHAR(100) NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        default_org_id NVARCHAR(64) NULL,
        last_login_at DATETIME2 NULL,
        remark NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

Recommended Index

    CREATE UNIQUE INDEX UX_sys_user_user_id
    ON sys_user(user_id)

    CREATE UNIQUE INDEX UX_sys_user_login_name
    ON sys_user(login_name)

---

# 5 Organization Table

Table Name

sys_org

Purpose

Stores enterprise organizational hierarchy.

Example hierarchy

Company  
Factory  
Workshop  
Team  

Fields

id  
Primary key

org_id  
Organization identifier

org_name  
Organization name

org_code  
Organization code

org_type  
company / factory / workshop / team

parent_org_id  
Parent organization

sort_no  
Sort order

status  
active / disabled

remark  
Remarks

created_at  
Created time

created_by  
Created by

updated_at  
Updated time

updated_by  
Updated by

SQL Example

    CREATE TABLE sys_org (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        org_id NVARCHAR(64) NOT NULL,
        org_name NVARCHAR(100) NOT NULL,
        org_code NVARCHAR(100) NULL,
        org_type NVARCHAR(50) NOT NULL,
        parent_org_id NVARCHAR(64) NULL,
        sort_no INT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        remark NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

Recommended Index

    CREATE UNIQUE INDEX UX_sys_org_org_id
    ON sys_org(org_id)

    CREATE INDEX IX_sys_org_parent_org_id
    ON sys_org(parent_org_id)

---

# 6 Role Table

Table Name

sys_role

Purpose

Stores role definitions.

Fields

id  
Primary key

role_id  
Role identifier

role_code  
Role code

role_name  
Role display name

role_type  
business / system

status  
active / disabled

remark  
Remarks

created_at  
Created time

created_by  
Created by

updated_at  
Updated time

updated_by  
Updated by

SQL Example

    CREATE TABLE sys_role (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        role_id NVARCHAR(64) NOT NULL,
        role_code NVARCHAR(100) NOT NULL,
        role_name NVARCHAR(100) NOT NULL,
        role_type NVARCHAR(50) NOT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        remark NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

---

# 7 Permission Table

Table Name

sys_permission

Purpose

Stores atomic system permissions.

Permission naming rule

resource:action

Examples

dashboard:view  
tool:search  
order:create  
order:submit  
order:keeper_confirm  

SQL Example

    CREATE TABLE sys_permission (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        permission_code NVARCHAR(100) NOT NULL,
        permission_name NVARCHAR(100) NOT NULL,
        resource_name NVARCHAR(100) NOT NULL,
        action_name NVARCHAR(100) NOT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        remark NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

---

# 8 User Role Relation

Table Name

sys_user_role_rel

Purpose

Assigns roles to users.

SQL Example

    CREATE TABLE sys_user_role_rel (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        user_id NVARCHAR(64) NOT NULL,
        role_id NVARCHAR(64) NOT NULL,
        org_id NVARCHAR(64) NULL,
        is_primary BIT NOT NULL DEFAULT 0,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

---

# 9 Role Permission Relation

Table Name

sys_role_permission_rel

Purpose

Maps roles to permissions.

SQL Example

    CREATE TABLE sys_role_permission_rel (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        role_id NVARCHAR(64) NOT NULL,
        permission_code NVARCHAR(100) NOT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

---

# 10 Role Data Scope Relation

Table Name

sys_role_data_scope_rel

Purpose

Defines the data scope allowed for each role.

Scope Types

ALL  
ORG  
ORG_AND_CHILDREN  
SELF  
ASSIGNED  
CUSTOM

SQL Example

    CREATE TABLE sys_role_data_scope_rel (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        role_id NVARCHAR(64) NOT NULL,
        scope_type NVARCHAR(50) NOT NULL,
        scope_value NVARCHAR(500) NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )

---

# End of Document