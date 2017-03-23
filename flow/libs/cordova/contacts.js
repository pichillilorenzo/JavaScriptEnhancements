type ContactAddress = {
  pref: ?boolean;
  type: string;
  formatted: ?string;
  streetAddress: string;
  locality: string;
  region: string;
  postalCode: string;
  country: string;
}

type UNKNOWN_ERROR = 0;
type INVALID_ARGUMENT_ERROR = 1;
type TIMEOUT_ERROR = 2;
type PENDING_OPERATION_ERROR = 3;
type IO_ERROR = 4;
type NOT_SUPPORTED_ERROR = 5;
type OPERATION_CANCELLED_ERROR = 6;
type PERMISSION_DENIED_ERROR = 20;

type ContactError = {
  UNKNOWN_ERROR: UNKNOWN_ERROR;
  INVALID_ARGUMENT_ERROR: INVALID_ARGUMENT_ERROR;
  TIMEOUT_ERROR: TIMEOUT_ERROR;
  PENDING_OPERATION_ERROR: PENDING_OPERATION_ERROR;
  IO_ERROR: IO_ERROR;
  NOT_SUPPORTED_ERROR: NOT_SUPPORTED_ERROR;
  OPERATION_CANCELLED_ERROR: OPERATION_CANCELLED_ERROR;
  PERMISSION_DENIED_ERROR: PERMISSION_DENIED_ERROR;

  code: UNKNOWN_ERROR | INVALID_ARGUMENT_ERROR | TIMEOUT_ERROR | PENDING_OPERATION_ERROR | PENDING_OPERATION_ERROR | IO_ERROR | NOT_SUPPORTED_ERROR | OPERATION_CANCELLED_ERROR | PERMISSION_DENIED_ERROR;
}

type ContactField = {
  type: string;
  value: string;
  pref: ?boolean;
}

type ContactName = {
  formatted: string;
  familyName: ?string;
  givenName: ?string;
  middleName: ?string;
  honorificPrefix: ?string;
  honorificSuffix: ?string;
}

type ContactOrganization = {
  pref: ?boolean;
  type: ?string;
  name: string;
  department: ?string;
  title: string;
}

type ContactRemoveOnSuccessEventHandler = (message: string) => void;
type ContactRemoveOnErrorEventHandler = (message: string) => void;

type ContactSaveOnSuccessEventHandler = (message: string) => void;
type ContactSaveOnErrorEventHandler = (message: string) => void;

declare class Contact {
  id: string;
  displayName: ?string;
  name: ContactName;
  nickname: string;
  phoneNumbers: ContactField[];
  emails: ContactField[];
  addresses: ContactAddress[];
  ims: ?ContactField[];
  organizations: ContactOrganization[];
  birthday: ?string;
  note: ?string;
  photos: ?ContactField[];
  categories: ?ContactField[];
  urls: ContactField[];
  clone(): Contact;
  remove(onSuccess?: ContactRemoveOnSuccessEventHandler, onError?: ContactRemoveOnErrorEventHandler): ?void;
  save(onSuccess?: ContactSaveOnSuccessEventHandler, onError?: ContactSaveOnErrorEventHandler): void;
}