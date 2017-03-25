type BatteryStatus = {
  level: number;
  isPlugged(): boolean;
}

type BatteryStatusEventHandler = (status: BatteryStatus) => mixed
type BatteryStatusEventListener = {handleEvent: BatteryStatusEventHandler} | BatteryStatusEventHandler

type BatteryStatusType = 'batterystatus' | 'batterycritical' | 'batterylow'
