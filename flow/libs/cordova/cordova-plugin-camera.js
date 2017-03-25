type DestinationType = { 
  DATA_URL: number;
  FILE_URI: number;
  NATIVE_URI: number;
}

type EncodingType = {
  JPEG: number;
  PNG: number;
}

type MediaType = {
  PICTURE: number;
  VIDEO: number;
  ALLMEDIA: number;
}

type PictureSourceType = {
  PHOTOLIBRARY: number;
  CAMERA: number;
  SAVEDPHOTOALBUM: number;
}

type PopoverArrowDirection = {
  ARROW_UP: number;
  ARROW_DOWN: number;
  ARROW_LEFT: number;
  ARROW_RIGHT: number;
  ARROW_ANY: number;
}

type Direction = {
  BACK: number;
  FRONT: number;
}

declare class CameraPopoverOptions {
  constructor(x?: number, y?: number, width?: number, height?: number, arrowDir?: number): void;
}

declare class CameraPopoverHandle {
  constructor(): void;
  setPosition(cameraPopoverOptions: CameraPopoverOptions): void;
}

declare var Camera: {
  quality: number;
  destinationType: DestinationType;
  sourceType: PictureSourceType;
  allowEdit: boolean;
  encodingType: EncodingType;
  targetWidth: number;
  targetHeight: number;
  mediaType: MediaType;
  correctOrientation: boolean;
  saveToPhotoAlbum: boolean;
  popoverOptions: CameraPopoverOptions;
  cameraDirection: Direction;
}

type CameraOnSuccessEventHandler = (message: string) => void;
type CameraOnErrorEventHandler = (message: string) => void;
