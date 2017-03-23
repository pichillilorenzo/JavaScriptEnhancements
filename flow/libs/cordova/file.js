declare var TEMPORARY: number; 

declare var LocalFileSystem: {
  PERSISTENT: number;
}

type FileEntry = {
  name: string;
  fullPath: string;
  isFile: boolean;

  toURL(): string;
  toInternalURL(): string;
}

type DirectoryEntry = {
  name: string;
  fullPath: string;
  isFile: boolean;

  getFile(path: string, obj: {create: boolean, exclusive: boolean}, callbackOnSuccess: (entry: FileEntry | DirectoryEntry) => void, callbackOnError: (error: Error) => void): void;
}

type FileSystem = {
  root: DirectoryEntry;
}

type resolveLocalFileSystemURLOnSuccessEventHandler = (entry: FileEntry | DirectoryEntry) => void;
type resolveLocalFileSystemURLOnErrorEventHandler = (error: Error) => void;

declare function resolveLocalFileSystemURL(
  url: string, 
  onSuccess?: resolveLocalFileSystemURLOnSuccessEventHandler, 
  onError?: resolveLocalFileSystemURLOnErrorEventHandler
): void;

type requestFileSystemOnSuccessEventHandler = (fs: FileSystem) => void;
type requestFileSystemOnErrorEventHandler = (error: Error) => void;

declare function requestFileSystem(
  storageType: typeof TEMPORARY | typeof LocalFileSystem.PERSISTENT,
  dimensions: number,
  onSuccess?: requestFileSystemOnSuccessEventHandler, 
  onError?: requestFileSystemOnErrorEventHandler
): void