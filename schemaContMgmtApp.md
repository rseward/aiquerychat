# Actual Schema
 
## DBO.ASPNETROLES
 
```
CREATE TABLE dbo.AspNetRoles (
  Id NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Name NVARCHAR(256) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.ASPNETUSERCLAIMS
 
```
CREATE TABLE dbo.AspNetUserClaims (
  Id INTEGER  
  UserId NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ClaimType NVARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ClaimValue NVARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.ASPNETUSERLOGINS
 
```
CREATE TABLE dbo.AspNetUserLogins (
  LoginProvider NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ProviderKey NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UserId NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.ASPNETUSERROLES
 
```
CREATE TABLE dbo.AspNetUserRoles (
  UserId NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  RoleId NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.ASPNETUSERS
 
```
CREATE TABLE dbo.AspNetUsers (
  Id NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Email NVARCHAR(256) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  EmailConfirmed BIT  
  PasswordHash NVARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  SecurityStamp NVARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  PhoneNumber NVARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  PhoneNumberConfirmed BIT  
  TwoFactorEnabled BIT  
  LockoutEndDateUtc DATETIME  
  LockoutEnabled BIT  
  AccessFailedCount INTEGER  
  UserName NVARCHAR(256) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.BUSINESSUNIT
 
```
CREATE TABLE dbo.BusinessUnit (
  Id INTEGER  
  BusinessUnitTypeId INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Address1 VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Address2 VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  City VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  State VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Zip VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Country VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Phone VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  AltPhone VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Fax VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ClientCourtId INTEGER  
  ParentLawFirmId INTEGER  
  ParentClientOwnerId INTEGER  
  SignupDate DATETIME  
  StatusId INTEGER  
  PrimaryContact INTEGER  
  AttorneyNamesOnDocument VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  EndDate DATETIME  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ParentLawFirmGroupId INTEGER  


)
```

## DBO.BUSINESSUNITDEFAULTCHARGE
 
```
CREATE TABLE dbo.BusinessUnitDefaultCharge (
  Id INTEGER  
  BusinessUnitId INTEGER  
  CaseTypeId INTEGER  
  CaseStateId INTEGER  
  CaseChargeTypeId INTEGER  
  ChargeName VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CaseChargeOccursAtId INTEGER  
  Qty INTEGER  
  Rate DECIMAL(18, 2)  
  Active BIT  
  CreateDate DATETIME  
  CreateBy VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.BUSINESSUNITPAYABLE
 
```
CREATE TABLE dbo.BusinessUnitPayable (
  Id INTEGER  
  BusinessUnitId INTEGER  
  PayableName VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.BUSINESSUNITSTATUS
 
```
CREATE TABLE dbo.BusinessUnitStatus (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.BUSINESSUNITTYPE
 
```
CREATE TABLE dbo.BusinessUnitType (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.CASE
 
```
CREATE TABLE dbo.Case (
  Id INTEGER  
  ClientId INTEGER  
  ClientContactId INTEGER  
  CaseTypeId INTEGER  
  FirstName VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  LastName VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  OtherOccupantNames VARCHAR(500) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Phone VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Address1 VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Address2 VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  City VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  State VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Zip VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Country VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CaseStateId INTEGER  
  CourtDateTime DATETIME  
  DefendantsCount INTEGER  
  CaseNumber VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  JudgementDate DATETIME  
  AppealDate DATETIME  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  


)
```

## DBO.CASEACTIVITY
 
```
CREATE TABLE dbo.CaseActivity (
  Id INTEGER  
  CaseId INTEGER  
  ActivityCategoryId INTEGER  
  Detail VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.CASEACTIVITYCATEGORY
 
```
CREATE TABLE dbo.CaseActivityCategory (
  Id INTEGER  
  Code VARCHAR(20) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  


)
```

## DBO.CASECHARGEOCCURSAT
 
```
CREATE TABLE dbo.CaseChargeOccursAt (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.CASECHARGETYPE
 
```
CREATE TABLE dbo.CaseChargeType (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  


)
```

## DBO.CASEDOCUMENT
 
```
CREATE TABLE dbo.CaseDocument (
  Id INTEGER  
  CaseId INTEGER  
  CaseStateId INTEGER  
  Name VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Path VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  Notes VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  


)
```

## DBO.CASENOTES
 
```
CREATE TABLE dbo.CaseNotes (
  Id INTEGER  
  CaseId INTEGER  
  Notes VARCHAR(5000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  


)
```

## DBO.CASESTATE
 
```
CREATE TABLE dbo.CaseState (
  Id INTEGER  
  Code VARCHAR(20) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Name VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(500) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  


)
```

## DBO.CASESTATEDATA
 
```
CREATE TABLE dbo.CaseStateData (
  Id INTEGER  
  CaseId INTEGER  
  CaseStateId INTEGER  
  JsonDataType VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  JsonData TEXT(2147483647) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  


)
```

## DBO.CASETYPE
 
```
CREATE TABLE dbo.CaseType (
  Id INTEGER  
  Code VARCHAR(20) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Name VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  


)
```

## DBO.CASETYPESTATEFLOW
 
```
CREATE TABLE dbo.CaseTypeStateFlow (
  Id INTEGER  
  CaseTypeId INTEGER  
  CaseFromStateId INTEGER  
  CaseToStateId INTEGER  
  Description VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  


)
```

## DBO.CASETYPESTATEFLOWPERMISSION
 
```
CREATE TABLE dbo.CaseTypeStateFlowPermission (
  BusinessUnitTypeId INTEGER  
  CaseTypeStateFlowId INTEGER  


)
```

## DBO.CHECKREQUEST
 
```
CREATE TABLE dbo.CheckRequest (
  Id INTEGER  
  ClientId INTEGER  
  BusinessUnitPayableId INTEGER  
  CourtDate DATETIME  
  FiledDate DATETIME  
  CheckRequestStatusId INTEGER  
  ReceivedDate DATETIME  
  CheckNo VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CheckAmount DECIMAL(18, 2)  
  Notes VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.CHECKREQUESTLINEITEM
 
```
CREATE TABLE dbo.CheckRequestLineItem (
  CheckReqestId INTEGER  
  InvoiceLineItemId INTEGER  


)
```

## DBO.CHECKREQUESTSTATUS
 
```
CREATE TABLE dbo.CheckRequestStatus (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(250) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.INVOICE
 
```
CREATE TABLE dbo.Invoice (
  Id INTEGER  
  ClientId INTEGER  
  Amount DECIMAL(18, 2)  
  PaidAmount DECIMAL(18, 2)  
  InvoiceDate DATETIME  
  DueDate DATETIME  
  Notes VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  
  InvoiceTermId INTEGER  
  InvoiceById INTEGER  


)
```

## DBO.INVOICEDOCUMENT
 
```
CREATE TABLE dbo.InvoiceDocument (
  Id INTEGER  
  InvoiceId INTEGER  
  Path VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  Notes VARCHAR(1000) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.INVOICELINEITEM
 
```
CREATE TABLE dbo.InvoiceLineItem (
  Id INTEGER  
  CaseId INTEGER  
  BusinessUnitDefaultChargeId INTEGER  
  CaseStateId INTEGER  
  CaseChargeTypeId INTEGER  
  InvoiceId INTEGER  
  Quantity INTEGER  
  Rate DECIMAL(18, 2)  
  Discount DECIMAL(18, 2)  
  TotalAmount DECIMAL(18, 2)  
  Description VARCHAR(200) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Notes VARCHAR(500) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  ChargeDate DATETIME  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.INVOICEPAYMENT
 
```
CREATE TABLE dbo.InvoicePayment (
  Id INTEGER  
  InvoiceId INTEGER  
  PaymentId INTEGER  
  PaidAmount DECIMAL(18, 2)  
  Active BIT  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.INVOICETERM
 
```
CREATE TABLE dbo.InvoiceTerm (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Description VARCHAR(500) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Active BIT  
  TermDays INTEGER  


)
```

## DBO.PAYMENT
 
```
CREATE TABLE dbo.Payment (
  Id INTEGER  
  ClientId INTEGER  
  Amount DECIMAL(18, 2)  
  AmountLeft DECIMAL(18, 2)  
  PayMethod VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CheckNo VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  PaymentDate DATETIME  
  Active BIT  
  Notes VARCHAR(500) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CreateDate DATETIME  
  CreateById INTEGER  
  UpdateDate DATETIME  
  UpdateById INTEGER  


)
```

## DBO.USER
 
```
CREATE TABLE dbo.User (
  Id INTEGER  
  AspUetUserId NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  BusinessUnitId INTEGER  
  FirstName VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  LastName VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Phone VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  AltPhone VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Fax VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Email VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  StatusId INTEGER  
  AttorneyBarNum VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  CreateDate DATETIME  
  CreateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  UpdateDate DATETIME  
  UpdateBy VARCHAR(100) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.USERROLE
 
```
CREATE TABLE dbo.UserRole (
  Id INTEGER  
  BusinessUnitTypeId INTEGER  
  Code VARCHAR(20) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.USERSTATUS
 
```
CREATE TABLE dbo.UserStatus (
  Id INTEGER  
  Name VARCHAR(50) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.USERXUSERROLE
 
```
CREATE TABLE dbo.UserXUserRole (
  UserId INTEGER  
  UserRoleId INTEGER  


)
```

## DBO.__MIGRATIONHISTORY
 
```
CREATE TABLE dbo.__MigrationHistory (
  MigrationId NVARCHAR(150) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  ContextKey NVARCHAR(300) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  Model VARBINARY  
  ProductVersion NVARCHAR(32) COLLATE "SQL_Latin1_General_CP1_CI_AS"  


)
```

## DBO.SYSDIAGRAMS
 
```
CREATE TABLE dbo.sysdiagrams (
  name NVARCHAR(128) COLLATE "SQL_Latin1_General_CP1_CI_AS"  
  principal_id INTEGER  
  diagram_id INTEGER  
  version INTEGER  
  definition VARBINARY  


)
```
