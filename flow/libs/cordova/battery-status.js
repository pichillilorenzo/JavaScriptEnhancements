declare class BatteryStatus {
  level: number;
  static isPlugged(): boolean;
}

type BatteryStatusEventHandler = (status: BatteryStatus) => mixed
type BatteryStatusEventListener = {handleEvent: BatteryStatusEventHandler} | BatteryStatusEventHandler

type BatteryStatusType = 'batterystatus' | 'batterycritical' | 'batterylow'

declare class EventTarget {
  addEventListener(type: MouseEventTypes, listener: MouseEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: KeyboardEventTypes, listener: KeyboardEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: TouchEventTypes, listener: TouchEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: WheelEventTypes, listener: WheelEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: ProgressEventTypes, listener: ProgressEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: DragEventTypes, listener: DragEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: AnimationEventTypes, listener: AnimationEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  addEventListener(type: BatteryStatusType, listener: BatteryStatusEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void; // BatteryStatus
  addEventListener(type: string, listener: EventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;

  removeEventListener(type: MouseEventTypes, listener: MouseEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: KeyboardEventTypes, listener: KeyboardEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: TouchEventTypes, listener: TouchEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: WheelEventTypes, listener: WheelEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: ProgressEventTypes, listener: ProgressEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: DragEventTypes, listener: DragEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: AnimationEventTypes, listener: AnimationEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;
  removeEventListener(type: BatteryStatusType, listener: BatteryStatusEventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void; // BatteryStatus
  removeEventListener(type: string, listener: EventListener, optionsOrUseCapture?: EventListenerOptionsOrUseCapture): void;

  attachEvent?: (type: MouseEventTypes, listener: MouseEventListener) => void;
  attachEvent?: (type: KeyboardEventTypes, listener: KeyboardEventListener) => void;
  attachEvent?: (type: TouchEventTypes, listener: TouchEventListener) => void;
  attachEvent?: (type: WheelEventTypes, listener: WheelEventListener) => void;
  attachEvent?: (type: ProgressEventTypes, listener: ProgressEventListener) => void;
  attachEvent?: (type: DragEventTypes, listener: DragEventListener) => void;
  attachEvent?: (type: AnimationEventTypes, listener: AnimationEventListener) => void;
  attachEvent?: (type: string, listener: EventListener) => void;

  detachEvent?: (type: MouseEventTypes, listener: MouseEventListener) => void;
  detachEvent?: (type: KeyboardEventTypes, listener: KeyboardEventListener) => void;
  detachEvent?: (type: TouchEventTypes, listener: TouchEventListener) => void;
  detachEvent?: (type: WheelEventTypes, listener: WheelEventListener) => void;
  detachEvent?: (type: ProgressEventTypes, listener: ProgressEventListener) => void;
  detachEvent?: (type: DragEventTypes, listener: DragEventListener) => void;
  detachEvent?: (type: AnimationEventTypes, listener: AnimationEventListener) => void;
  detachEvent?: (type: string, listener: EventListener) => void;

  dispatchEvent(evt: Event): boolean;

  // Deprecated

  cancelBubble: boolean;
  initEvent(eventTypeArg: string, canBubbleArg: boolean, cancelableArg: boolean): void;
}