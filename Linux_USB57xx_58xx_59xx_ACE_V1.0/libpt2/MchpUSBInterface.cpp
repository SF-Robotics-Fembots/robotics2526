/*
**********************************************************************************
* © 2015 Microchip Technology Inc. and its subsidiaries.
* You may use this software and any derivatives exclusively with
* Microchip products.
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS".
* NO WARRANTIES, WHETHER EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE,
* INCLUDING ANY IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY,
* AND FITNESS FOR A PARTICULAR PURPOSE, OR ITS INTERACTION WITH MICROCHIP
* PRODUCTS, COMBINATION WITH ANY OTHER PRODUCTS, OR USE IN ANY APPLICATION.
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE.
* TO THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL
* CLAIMS IN ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF
* FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
* MICROCHIP PROVIDES THIS SOFTWARE CONDITIONALLY UPON YOUR ACCEPTANCE
* OF THESE TERMS.
**********************************************************************************
*  $Revision: #1.1 $  $DateTime: 2015/09/21 04:18:20 $  $    $
*  Description: This version supports SPI,I2C,UART Bridging and Programming Config file
**********************************************************************************
* $File:  MchpUSBINterface.cpp
*/

#include <stdio.h>
#include <libusb.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <math.h>
#include "MchpUSBInterface.h"
#include "USB2740_SpiFlash.h"
#include "USBHubAbstraction.h"

#define FALSE								0
#define TRUE								1	
#define min(a,b)							(((a) < (b)) ? (a) : (b))
#define MICROCHIP_HUB_VID						0x424



#define VID_MICROCHIP							0x0424
#define PID_HCE_DEVICE							0x2740



#define PIO32_DIR_ADDR   						0x0830
#define PIO32_OUT_ADDR							0x0834
#define PIO32_IN_ADDR							0x0838 

#define PIO64_DIR_ADDR   						0x0930
#define PIO64_OUT_ADDR							0x0934
#define PIO64_IN_ADDR							0x0938 

#define PIODIR_ADDR_OFFSET   						0x30
#define PIOOUT_ADDR_OFFSET 						0x34
#define PIOIN_ADDR_OFFSET 						0x38 
#define PIO64_BASE_ADDRESS						0x900
#define PIO32_BASE_ADDRESS						0x800

#define PIO_INP_EN_ADDR							0x80
#define	 LED0_PIO0_CTL_0						0x0806
#define	 LED0_PIO0_CTL_0_XNOR						0x80
#define	 LED0_PIO0_CTL_0_MODE						0x40
#define	 LED0_PIO0_CTL_0_RATE						0x3F

#define	 LED0_PIO0_CTL_1						0x0807
#define	 LED0_PIO0_CTL_1_TRAIL_OFF					0xFC
#define	 LED0_PIO0_CTL_1_LED_ON						0x02
#define	 LED0_PIO0_CTL_1_LED_PIO					0x01

#define	 LED1_PIO1_CTL_0						0x0808
#define	 LED1_PIO1_CTL_0_XNOR						0x80
#define	 LED1_PIO1_CTL_0_MODE						0x40
#define	 LED1_PIO1_CTL_0_RATE						0x3F

#define	 LED1_PIO1_CTL_1						0x0809
#define	 LED1_PIO1_CTL_1_TRAIL_OFF					0xFC
#define	 LED1_PIO1_CTL_1_LED_ON						0x02
#define	 LED1_PIO1_CTL_1_LED_PIO					0x01

#define SUSP_SEL							0x3C52
#define SUSP_SEL_SUSP_SEL						0x01

#define	 CHRG_DET_BYPASS						0x3C50
#define  CHRGEDET_BYPASS_BIT						0x80

#define  BOND_OPT0							0x0802
#define  BOND_OPT0_OPTRESEN						0x80
#define  BOND_OPT0_PKG_TYPE						0x18



#define  PORT_SEL1							0x3C00
#define  PORT_SEL2							0x3C04
#define  PORT_SEL3							0x3C08
#define  PORT_SEL4							0x3C0C
#define  VBUS_PASS_THRU							0x3C40
#define  PORT_DISABLE_GPIO_EN_VAL					0x04
#define	 VBUS_GPIO_VAL							0x02

// USB57X4 GPIO
#define PF1_CTL								0x0A11
#define PF2_CTL								0x0A12
#define PF3_CTL								0x0A13
#define PF4_CTL								0x0A14
#define PF5_CTL								0x0A15
#define PF6_CTL								0x0A16
#define PF7_CTL								0x0A17

#define UART_ACTV							0x0B11

#define MAX_OTP_READ_SIZE						0x400

#define  UTIL_CONFIG1_ADDR						0x080A
#define  UTIL_CONFIG1_SOFENABLE						0x80
#define  UTIL_CONFIG1_TXDSEL						0x20
#define  UTIL_CONFIG1_DEBUG_JTAG					0x10
#define  UTIL_CONFIG1_RXDSEL						0x08
#define  UTIL_CONFIG1_SPIMASTERDIS					0x04


#define I2C_ENTER_PASSTHRG						0x70
#define I2C_EXIT_PASSTHRG						0x73
#define I2C_READ							1
#define I2C_WRITE							0

#define I2C_READ_CMD							0x72
#define I2C_WRITE_CMD							0x71
#define I2CFL_SEND_STOP							0x01
#define I2CFL_SEND_START						0x02
#define I2CFL_SEND_NACK							0x04					

//USB2530 I2c Flags
#define SEND_NACK							0x04
#define SEND_START							0x02
#define SEND_STOP							0x01

#define I2C_READ_BIT 							0x01
#define CMD_I2C_WRITE							0x71
#define CMD_I2C_READ							0x72

#define	 I2C_CTL_ADDR							0x0954
#define I2C_CTL_BLK_MODE_EN						0x04
#define  I2C_CTL_EXTHWI2CEN						0x02
#define  I2C_CTL_INTI2CEN						0x01

//OTP
#define OTP_DATA_START_ADDRESS						0x0002
#define BIG_ENDIAN_WORD(w) 						((((w)&0xFF)<<8) | (((w)&0xFF00) >> 8))

#define	 OCS_SEL1							 0x3c20
#define	 OCS_SEL2							 0x3c24
#define	 OCS_SEL3							 0x3c28
#define	 OCS_SEL4							 0x3c2C

#define CONVERT_ENDIAN_DWORD(w)	((((DWORD32)(w)) << 24) | (((DWORD32)(w) & 0xFF00) << 8) | \
								 (((DWORD32)(w) & 0xFF0000) >> 8) | (((DWORD32)(w) & 0xFF000000) >> 24))

#define PT2_LIB_VER							"1.00.00"

#define CTRL_RETRIES 							2
#define HUB_STATUS_BYTELEN						3 /* max 3 bytes status = hub + 23 ports */
#define HUB_DESC_NUM_PORTS_OFFSET					2


#define logprint(x, ...) do { \
		printf(__VA_ARGS__); \
		fprintf(x,  __VA_ARGS__); \


//OTP
typedef struct tagOtpCfgChecksumA
{
	uint8_t	abyXORChecksum;
	uint16_t	wCfgStartOffset;
	uint16_t	wCfgLength;

}OTP_CFG_CHECKSUM;

typedef struct tagOtpCfgChecksumA1
{
	uint8_t	abySignature [3];
	OTP_CFG_CHECKSUM otpCfgChecksum;

}OTP_CFG_CHECKSUM_A1, *POTP_CFG_CHECKSUM_A1;	
		
/*-----------------------Helper functions --------------------------*/
int usb_enable_HCE_device(uint8_t hub_index);
static int compare_hubs(const void *p1, const void *p2);
static int usb_get_hubs(PHINFO pHubInfoList);
static int usb_open_HCE_device(uint8_t hub_index);
int  usb_send_vsm_command(struct libusb_device_handle *handle, uint8_t * byValue) ;
bool UsbSetBitXdata(int hub_index,WORD wXDataAddress,BYTE byBitToSet);
bool UsbClearBitXdata(int hub_index,WORD wXDataAddress,BYTE byBitToClear);
int Read_OTP(HANDLE handle, uint16_t wAddress, uint8_t *data, uint16_t num_bytes);
int Write_OTP(HANDLE handle, uint16_t wAddress, uint8_t *data, uint16_t num_bytes);
int xdata_read(HANDLE handle, uint16_t wAddress, uint8_t *data, uint8_t num_bytes);
int xdata_write(HANDLE handle, uint16_t wAddress, uint8_t *data, uint8_t num_bytes);
//I2C Bridging
int USB_I2C_Transfer(int hub_index,BOOL byDir,uint8_t byAddr, uint8_t *pbyBuffer, uint16_t wLength , uint32_t *wdActualLength);
BOOL Gen_I2C_Transfer (int hub_index, BOOL bDirection, BYTE* pbyBuffer, WORD wDataLen, BYTE bySlaveAddress,BOOL bStart,BOOL bStop,BOOL bNack);

//OTP Programming
unsigned int CalculateNumberofOnes(unsigned int UINTVar);

 // Global variable for tracking the list of hubs
HINFO gasHubInfo [MAX_HUBS];
/* Context Variable used for initializing LibUSB session */
libusb_context *ctx = NULL; 
WORD gwPID = 0x2734;;
/*-----------------------API functions --------------------------*/
BOOL  MchpUsbGetVersion ( PCHAR pchVersionNo )
{
	BOOL bRet = TRUE;
	
	//Send command to lib to get library version
	sprintf(pchVersionNo,"%s",PT2_LIB_VER);

	return bRet;

}

UINT32 MchpUsbGetLastErr (HANDLE DevID)
{
	return errno;
}
 
HANDLE  MchpUsbOpenID ( UINT16 wVID, UINT16 wPID)
{
	int error = 0, hub_cnt=0, hub_index=0;
	int restart_count=5;	
	bool bhub_found = false;
	gwPID = wPID;
	hub_cnt = usb_get_hubs(&gasHubInfo[0]);
	
	do
	{
		if((gasHubInfo[hub_index].wVID == wVID) && (gasHubInfo[hub_index].wPID == wPID))
		{
			bhub_found = true;
		}
	
	}
	while(hub_index++ < hub_cnt);
	
	if(false == bhub_found)
	{
		DEBUGPRINT("MCHP_Error_Device_Not_Found \n");
		return INVALID_HANDLE_VALUE;
	}

	error = usb_open_HCE_device(hub_index);
	if(error < 0)
	{
	
		//enable 5th Endpoit
		error = usb_enable_HCE_device(hub_index);
		
		if(error < 0)
		{
			DEBUGPRINT("MCHP_Error_Invalid_Device_Handle: Failed to Enable the device \n");
			return INVALID_HANDLE_VALUE;
		}
		do
		{
			sleep(2);
			error = usb_open_HCE_device(hub_index);
			if(error == 0)
			{
				return hub_index;	
			}
			
		}while(restart_count--);

		DEBUGPRINT("MCHP_Error_Invalid_Device_Handle: Failed to open the device error:%d\n",error);
		return INVALID_HANDLE_VALUE;
	}
	

	return hub_index;
}


BOOL MchpUsbClose(HANDLE DevID)
{
	
	if(gasHubInfo[DevID].handle != NULL) 
	{
		libusb_close((libusb_device_handle*)gasHubInfo[DevID].handle);
		gasHubInfo[DevID].dev = NULL;
		gasHubInfo[DevID].handle = NULL;
	}
	else
	{
		printf("unknown hub index%d\n", DevID);
		return false;
	}
	libusb_exit(ctx);
	return true;
}
BOOL  MchpUsbRegisterRead ( HANDLE DevID, UINT16 RegisterAddress, UINT16 BytesToRead, UINT8* InputData )
{
	int bRetVal = FALSE;
	USB_CTL_PKT UsbCtlPkt;
	
	/***************************USB57X4*******************************/
	bRetVal = libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle, 0x41,CMD_SET_MEM_TYPE,MEMTYPE_XDATA,0,0,0,CTRL_TIMEOUT);
	/*****************************************************************/

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[DevID].handle;
	UsbCtlPkt.byRequest = 0x04;
	UsbCtlPkt.wValue 	= RegisterAddress;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= InputData;
	UsbCtlPkt.wLength 	= BytesToRead;

	bRetVal = usb_HCE_read_data (&UsbCtlPkt);
	if(bRetVal < 0)
	{
		return false;	
	}
	return true;
}
BOOL  MchpUsbRegisterWrite( HANDLE DevID, UINT16 RegisterAddress,UINT16 BytesToWrite, UINT8* OutputData)
{
	int bRetVal = FALSE;
	if(nullptr == OutputData)
	{
		DEBUGPRINT("Register Write Failed: NULL Pointer\n");
		return false;
	}
	USB_CTL_PKT UsbCtlPkt;
	/***************************USB57X4*******************************/
	bRetVal = libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle, 0x41,CMD_SET_MEM_TYPE,MEMTYPE_XDATA,0,0,0,CTRL_TIMEOUT);
	/*****************************************************************/

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[DevID].handle;
	UsbCtlPkt.byRequest = 0x03;
	UsbCtlPkt.wValue 	= RegisterAddress;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= OutputData;
	UsbCtlPkt.wLength 	= BytesToWrite;

	bRetVal = usb_HCE_write_data (&UsbCtlPkt);
	if(bRetVal < 0)
	{
		return false;	
	}
	return true;
}
BOOL MchpUsbFlexConnect (HANDLE DevID, UINT16 Config)
{
	int bRetVal = FALSE;
	USB_CTL_PKT UsbCtlPkt;

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[DevID].handle;
	UsbCtlPkt.byRequest = 0x08;
	UsbCtlPkt.wValue 	= Config;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= 0;
	UsbCtlPkt.wLength 	= 0;

	bRetVal = usb_HCE_no_data(&UsbCtlPkt);
	if(bRetVal< 0)
	{
		DEBUGPRINT("Execute Enable Flex failed %d\n",bRetVal);
		return false;
	}
	return true;
}
BOOL MchpUsbGpioGet (HANDLE DevID, UINT8 PIONumber, UINT8* Pinstate)
{
	BOOL bRet = FALSE;
	WORD wBaseRegisterAddress = 0;

	DWORD dwInputData; 
	DWORD dwMask = 0;

	if(!((PIONumber <=12 && PIONumber >=1) || (PIONumber <=20 && PIONumber >=17)))
	{
		DEBUGPRINT ("Invalid GPIO Number \n");
		return bRet;
	}
	if (PIONumber > 31)
	{
		dwMask = (1 << (PIONumber - 32));
	}
	else
	{
		dwMask = (1 << PIONumber);
	}

	/*The base address is 0x800 for below 32 and 0x900 for upper32*/
	if(PIONumber > 32)
	{
		wBaseRegisterAddress = 0x900;
	}
	else
	{
		wBaseRegisterAddress = 0x800;
	}
	do
	{

			//Set direction offset to input
			bRet = MchpUsbRegisterRead( DevID, wBaseRegisterAddress + PIODIR_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
			if(FALSE == bRet)
			{
				DEBUGPRINT("MchpUsbGpioGet : Read direction Failed, Hubid : %d, PIONumber: %d",DevID,PIONumber);

				break;
			}
			//For input clear dir mask
			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) &~ dwMask;

			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData);


			bRet = MchpUsbRegisterWrite( DevID, wBaseRegisterAddress + PIODIR_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
			if(FALSE == bRet)
			{
				DEBUGPRINT("MchpUsbGpioGet : Set direction Failed, Hubid : %d, PIONumber: %d",DevID,PIONumber);
				break;
			}
			/******************************************USB57x4***************************************************************/
			bRet = MchpUsbRegisterRead( DevID, wBaseRegisterAddress + PIO_INP_EN_ADDR, 4, (BYTE *)&dwInputData);
			if(FALSE == bRet)
			{
				DEBUGPRINT( "MchpUsbGpioGet : Read OUT Reg Failed, Hubid : %d, PIONumber: %d",DevID,PIONumber);
				break;
			}
			//Enable Input here
			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) | dwMask;
		
			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData);
		
			bRet =	 MchpUsbRegisterWrite( DevID, wBaseRegisterAddress + PIO_INP_EN_ADDR, 4, (BYTE *)&dwInputData);	
			if(FALSE == bRet)
			{
				DEBUGPRINT( "MchpUsbGpioGet : Write dir mask Failed, Hubid : %d, PIONumber: %d",DevID,PIONumber);
				break;
			}
			/*****************************************************************************************************************/
			
			/*Read the PIO direction regsiter*/
			bRet = MchpUsbRegisterRead( DevID, (wBaseRegisterAddress + PIOIN_ADDR_OFFSET), 4, (BYTE *)&dwInputData);
			if(FALSE == bRet)
			{
				DEBUGPRINT("MchpUsbGpioGet : Write PIO direction Failed, Hubid : %d, PIONumber: %d",DevID,PIONumber);

				break;
			}
			
			(CONVERT_ENDIAN_DWORD (dwInputData) & dwMask)? (*Pinstate = 1) : (*Pinstate=0);
			DEBUGPRINT("MchpUsbGpioGet : Success, Hubid : %d, PIONumber: %d",DevID,PIONumber);

	}while(FALSE);


	return bRet;
}

 BOOL MchpUsbGpioSet (HANDLE DevID, UINT8 PIONumber, UINT8 Pinstate)
{
	BOOL bRet = FALSE;
	WORD wBaseRegisterAddress = 0;
	DWORD dwInputData; 
	DWORD dwMask = 0;

	if(!((PIONumber <=12 && PIONumber >=1) || (PIONumber <=20 && PIONumber >=17)))
	{
		DEBUGPRINT ("Invalid GPIO Number \n");
		return bRet;
	}
	if (PIONumber > 31)
	{
		dwMask = (1 << (PIONumber - 32));
	}
	else
	{
		dwMask = (1 << PIONumber);
	}

	/*The base address is 0x800 for below 32 and 0x900 for upper32*/
	if(PIONumber > 32)
	{
		wBaseRegisterAddress = 0x900;
	}
	else
	{
		wBaseRegisterAddress = 0x800;
	}
	
	
	do
	{
		
		//Set direction offset to ouput
		bRet = MchpUsbRegisterRead( DevID, wBaseRegisterAddress + PIODIR_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
		if(FALSE == bRet)
		{
			DEBUGPRINT("MchpUsbGpioSet : Read direction Failed, ,Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);
			break;
		}
		//For input clear dir mask
		dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) | dwMask;
		dwInputData = CONVERT_ENDIAN_DWORD (dwInputData);


		bRet = MchpUsbRegisterWrite( DevID, wBaseRegisterAddress + PIODIR_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
		if(FALSE == bRet)
		{
			DEBUGPRINT( "MchpUsbGpioSet : Write dir mask Failed, Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);

			break;
		}
		/******************************************USB57x4***************************************************************/
		bRet = MchpUsbRegisterRead( DevID, wBaseRegisterAddress + PIO_INP_EN_ADDR, 4, (BYTE *)&dwInputData);
		if(FALSE == bRet)
		{
			DEBUGPRINT( "MchpUsbGpioSet : Read OUT Reg Failed, Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);
			break;
		}
		//Enable Input here
		dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) &~ dwMask;
		
		dwInputData = CONVERT_ENDIAN_DWORD (dwInputData);
		
		bRet =	 MchpUsbRegisterWrite( DevID, wBaseRegisterAddress + PIO_INP_EN_ADDR, 4, (BYTE *)&dwInputData);	
		if(FALSE == bRet)
		{
			DEBUGPRINT( "MchpUsbGpioSet : Write dir mask Failed, Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);
			break;
		}
		/*****************************************************************************************************************/
		/*Read the OUT register*/
		bRet = MchpUsbRegisterRead( DevID, wBaseRegisterAddress + PIOOUT_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
		if(FALSE == bRet)
		{
			DEBUGPRINT( "MchpUsbGpioSet : Read OUT Reg Failed, Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);

			break;
		}

		/*Update the PIN state*/
		if(1 == Pinstate)
		{
			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) | dwMask;
		}
		else if(0 == Pinstate)
		{
			dwInputData = CONVERT_ENDIAN_DWORD (dwInputData) &~ dwMask;
		}
		else{
			DEBUGPRINT("Invalid Pin State \n");
			return false;
		}
		
		dwInputData = CONVERT_ENDIAN_DWORD (dwInputData);


		bRet = MchpUsbRegisterWrite( DevID, wBaseRegisterAddress + PIOOUT_ADDR_OFFSET, 4, (BYTE *)&dwInputData);
		if(FALSE == bRet)
		{
			DEBUGPRINT( "MchpUsbGpioSet : Failed, Hubid : %d, PIONumber: %d, Pinstate: %d",DevID,PIONumber,Pinstate);

			break;
		}
		DEBUGPRINT( "MchpUsbGpioSet : Success, Hubid : %d, PIONumber: %d,Pinstate: %d",DevID,PIONumber,Pinstate);

		bRet = TRUE;
		break;
			
		
	}while(FALSE);


	return bRet;
}
BOOL MchpUsbConfigureGPIO (HANDLE DevID, UINT8 PIONumber)
{
	BOOL bRet = FALSE;

	BYTE byTemp = 0x00;
	BOOL bValidGPIO = false;
	switch(PIONumber)
	{
		case 1:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF1_CTL, 1, &byTemp) ;
			break;

		case 2:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF2_CTL, 1, &byTemp) ;
			break;

		case 3:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF3_CTL, 1, &byTemp) ;
			break;

		case 4:
			//SPI_CLK / UART_RX /TCK
			//Disable uart_rx
			bValidGPIO = true;
			bRet = UsbClearBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_RXDSEL);
			if (!bRet)
			{
				break;
			}
			// Disable DEBUG_JTAG
			bRet = UsbClearBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_DEBUG_JTAG);
			if (!bRet)
			{
				break;
			}
			//Disable UART block
			bRet= MchpUsbRegisterWrite( DevID, UART_ACTV, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			
			// Disable SPI (set spi_master_dis)
			bRet = UsbSetBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_SPIMASTERDIS);
			break;

		case 5:
			//SPI_CLK / UART_RX /TCK
			//Disable uart_tx
			bValidGPIO = true;
			bRet = UsbClearBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_TXDSEL);
			if (!bRet)
			{
				break;
			}
			
			//Disable UART block
			bRet = UsbClearBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_DEBUG_JTAG);
			if (!bRet)
			{
				break;
			}

			//Disable UART block
			bRet= MchpUsbRegisterWrite( DevID, UART_ACTV, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}

			// Disable SPI (set spi_master_dis)
			bRet = UsbSetBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_SPIMASTERDIS);
			break;

		case 6:
			//SMDAT/ Prog Func 4
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF4_CTL, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet = UsbClearBitXdata(DevID, I2C_CTL_ADDR,(I2C_CTL_BLK_MODE_EN | I2C_CTL_INTI2CEN));
			break;

		case 7:
			//SPI_CE / CFG_NONREM
			// Disable SPI (set spi_master_dis)
			bValidGPIO = true;
			bRet = UsbSetBitXdata(DevID,UTIL_CONFIG1_ADDR,UTIL_CONFIG1_SPIMASTERDIS);
			break;

		case 8:
			// SMCLK /Prog Func 5
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF5_CTL, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet = UsbClearBitXdata(DevID, I2C_CTL_ADDR,(I2C_CTL_BLK_MODE_EN | I2C_CTL_INTI2CEN));
			break;

		case 9:
			//SPI_DI / TDI / CFG_BC_EN
			// DIsable SPI (set spi_master_dis)
			bValidGPIO = true;
			bRet = UsbSetBitXdata(DevID,UTIL_CONFIG1_ADDR, UTIL_CONFIG1_SPIMASTERDIS);
			if (!bRet)
			{
				break;
			}
			
			//Disable DEBUG_JTAG
			bRet = UsbClearBitXdata(DevID, UTIL_CONFIG1_ADDR, UTIL_CONFIG1_DEBUG_JTAG);
			break;

		case 10:
			// FLEXCONNECT / Prog Func 6
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF6_CTL, 1, &byTemp) ;
			break;

		case 11:
			// Prog Funct 7
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PF7_CTL, 1, &byTemp) ;
			break;

		case 12:
			// CFG_STRAP
			bValidGPIO = true;
			bRet= true;
			break;

		case 17:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PORT_SEL1, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet= MchpUsbRegisterWrite( DevID, OCS_SEL1, 1, &byTemp) ;
			break;

		case 18:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PORT_SEL2, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet= MchpUsbRegisterWrite( DevID, OCS_SEL2, 1, &byTemp) ;
			break;

		case 19:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PORT_SEL3, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet= MchpUsbRegisterWrite( DevID, OCS_SEL3, 1, &byTemp) ;
			break;

		case 20:
			bValidGPIO = true;
			bRet= MchpUsbRegisterWrite( DevID, PORT_SEL4, 1, &byTemp) ;
			if (!bRet)
			{
				break;
			}
			bRet= MchpUsbRegisterWrite( DevID, OCS_SEL4, 1, &byTemp) ;
			break;
	}
	if(false == bValidGPIO && false == bRet)
	{
		DEBUGPRINT("Invalid Pin Number \n");
		bRet = FALSE;
	}
	return bRet;
}
BOOL MchpUsbI2CSetConfig(HANDLE DevID,INT CRValue,INT nValue)
{
	int bRetval = FALSE;
	UINT16 wFreq = 0;
	do
	{
		if(nValue)
		{
			switch(nValue)
			{
				case 0x1:
					//62Khz
					wFreq = 0x0080;
					break;
				case 0x2:
					//235KHz
					wFreq = 0x0000; 
					break;
				case 0x3:
					//268KHz
					wFreq = 0x0001;
					break;
				case 0x4:
					//312kHz
					wFreq = 0x0002;
					break;
				case 0x5:
					//375KHz
					wFreq = 0x0003;
					break;
				default:
					break;
			}
		}
		else
		{
			wFreq = 256 - (625/CRValue);
			wFreq <<= 8;
			wFreq |= 0x83;
		}	
		bRetval= libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle,0x41,I2C_ENTER_PASSTHRG,0,wFreq,NULL,0,20);
		if(bRetval < 0)
		{
			DEBUGPRINT("Failed to set Frequency");
			bRetval = FALSE;
			break;
		}
		DEBUGPRINT ("Frequency Set : Success");
		bRetval = TRUE;
		break;
	}while(FALSE);
	return bRetval;
}
BOOL MchpUsbI2CRead (HANDLE DevID, INT BytesToRead, UINT8* InputData, UINT8 SlaveAddress)
{
	BOOL bRet = FALSE;
	UINT32 wdActualLength = 0;

	do
	{
		bRet = USB_I2C_Transfer(DevID, I2C_READ, SlaveAddress, InputData, BytesToRead, (uint32_t *)&wdActualLength);
	}while(FALSE);
	return bRet;
}
BOOL MchpUsbI2CWrite (HANDLE DevID, INT BytesToWrite, UINT8* OutputData, UINT8 SlaveAddress)
{
	BOOL bRet = FALSE;
	UINT32 wdActualLength = 0;
	if(nullptr == OutputData)
	{
		DEBUGPRINT("I2C Write Failed: NULL Pointer\n");
		return false;
	}
	do
	{
		bRet = USB_I2C_Transfer((int)DevID, I2C_WRITE, SlaveAddress, OutputData, BytesToWrite,(uint32_t *) &wdActualLength);
	}while(FALSE);
	return bRet;
}
BOOL MchpUsbI2CTransfer (HANDLE DevID, BOOL bDirection, UINT8* pbyBuffer, UINT16 wDataLen, UINT8 bySlaveAddress,BOOL bStart,BOOL bStop,BOOL bNack)
{
	BOOL bRet = FALSE;
	if(nullptr == pbyBuffer)
	{
		DEBUGPRINT("I2C Transfer Failed: NULL Pointer\n");
		return false;
	}
	
	bRet = Gen_I2C_Transfer(DevID,bDirection,pbyBuffer,wDataLen,bySlaveAddress,bStart,bStop,bNack);
	if(bRet == FALSE)
	{
		DEBUGPRINT("I2C Transfer Failed \n");
	}
	else
	{
		DEBUGPRINT("I2C Transfer Success \n");
	}
	return bRet;
}
BOOL MchpUsbSpiSetConfig ( HANDLE DevID, INT EnterExit)
{
	int rc = FALSE;
	BOOL bRet = FALSE;
	BYTE byCmd =0;

	if(EnterExit)
	{
		byCmd = CMD_SPI_PASSTHRU_ENTER;	
	}
	else
	{
		byCmd = CMD_SPI_PASSTHRU_EXIT;	
	}
	rc = libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle,0x41,byCmd,0,0,0,0,500);
	if(rc < 0)
	{
		DEBUGPRINT("MchpUsbSpiSetConfig failed\n");
		bRet = FALSE;
	}
	else
	{
		DEBUGPRINT("MchpUsbSpiSetConfig Passed\n");
		bRet = TRUE;
	}
	return bRet;
}
BOOL MchpUsbSpiFlashRead(HANDLE DevID,UINT32 StartAddr,UINT8* InputData,UINT32 BytesToRead)
{
	BOOL bRet = FALSE;

	if ((StartAddr + BytesToRead) > MAX_FW_SIZE)
	{
		DEBUGPRINT("MchpUsbSpiFlashRead Failed: BytesToRead (%d) and StartAddr(0x%x) is larger than SPI memory size\n",BytesToRead,StartAddr);
		return bRet;
	}
	//boots from SPI
	bRet = AthensReadSPIFlash(DevID,InputData,StartAddr,(StartAddr + BytesToRead));
	
	if(FALSE == bRet)
	{
		DEBUGPRINT("MchpUsbSpiFlashRead Failed \n");
	}
	else
	{
		DEBUGPRINT("MchpUsbSpiFlashRead Passed \n");
		bRet = TRUE;
	}
	return bRet;
}
BOOL MchpUsbSpiFlashWrite(HANDLE DevID,UINT32 StartAddr,UINT8* OutputData, UINT32 BytesToWrite)
{
	BOOL bRet = FALSE;
	if(nullptr == OutputData)
	{
		DEBUGPRINT("SPI Write Failed: NULL Pointer\n");
		return false;
	}
	if ((StartAddr + BytesToWrite) > MAX_FW_SIZE)
	{
		DEBUGPRINT("MchpUsbSpiFlashWrite Failed: BytesToWrite (%d) and StartAddr(0x%x) is larger than SPI memory size\n",BytesToWrite,StartAddr);
		return bRet;
	}
	bRet = WriteSPIFlash(DevID,OutputData,5000,TRUE,StartAddr,BytesToWrite);
	
	if(FALSE == bRet)
	{
		DEBUGPRINT("MchpUsbSpiFlashWrite failed \n");
	}
	else
	{
		DEBUGPRINT("MchpUsbSpiFlashWrite success \n");
		bRet = TRUE;
	}
	//Reset the device.
	uint8_t byData = 0;
	xdata_read(DevID, 0x804, &byData, 1);

	byData|= 0x04;
	xdata_write(DevID, 0x804, &byData, 1);

	byData = 0x40;
	xdata_write(DevID, 0x80A, &byData, 1);

	return bRet;
}
BOOL MchpUsbSpiTransfer(HANDLE DevID,INT Direction,UINT8* Buffer, UINT16 DataLength,UINT32 TotalLength)
{
	int bRetVal = FALSE;
	if(nullptr == Buffer)
	{
		DEBUGPRINT("SPI Transfer Failed: NULL Pointer\n");
		return false;
	}
	if(Direction) //Read
	{
		bRetVal = libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle,0xC1,0x04,(0x4A10),0,Buffer,
					TotalLength,CTRL_TIMEOUT);
	}
	else //Write
	{
		bRetVal = libusb_control_transfer((libusb_device_handle*)gasHubInfo[DevID].handle,0x41,0x61,TotalLength,0,Buffer,
					DataLength,CTRL_TIMEOUT);
	}
	if(bRetVal <0 )
	{
		DEBUGPRINT("SPI Transfer Failed \n");
		return FALSE;
	}
	else
	{
		DEBUGPRINT("SPI Transfer success \n ");
		return TRUE;
	}
	
}
BOOL MchpProgramFile( HANDLE DevID, PCHAR InputFileName)
{
	BOOL bRet = FALSE;
	//Read entire OTP
	uint8_t *abyBuffer;
	uint8_t  pbyBuffer[64];
	uint32_t wDataLength;
	int rc = FALSE;
	uint16_t wConfigBytes;
	uint16_t wNumberOfOnes;
	WORD wReadLength,wTemp,wStartAddress;
	wDataLength = ReadBinfile(InputFileName,pbyBuffer);
	if(0 == wDataLength)
	{
		DEBUGPRINT("Failed to Read Given Configuration File \n");
		return bRet;
	}
	abyBuffer = (BYTE *) malloc (1024 * 8);
	//find whether device boots from SPI or ROM
	rc =Get_Hub_Info(DevID, (uint8_t *)&gasHubInfo[DevID].sHubInfo);

	unsigned int byReadData =0;
	if (FALSE ==MchpUsbRegisterRead(DevID,0x411D,1, (UINT8 *)&byReadData))
	{
		DEBUGPRINT("Read failed");
	}
	if(byReadData & 0x02)
	{
		byReadData &= ~0x04;
		if(FALSE ==MchpUsbRegisterWrite(DevID,0x411D,1,(UINT8 *) &byReadData))
		{
			DEBUGPRINT("Write failed");
		}
	}
	
	bRet= Read_OTP(DevID, wStartAddress, abyBuffer, (1024 * 8));
	writeBinfile("read.bin",  abyBuffer, (1024 * 8));
	

	// Update Number of configuration updated in OTP
	//Note that by default 0th byte is 0x00 and 1st byte is 0xff present in the OTP.
	//That is why xor is used below command
	if(gasHubInfo[DevID].sHubInfo.byFeaturesFlag & 0x01)
	{
		wConfigBytes = (abyBuffer[0] << 8) | (abyBuffer[1]);
		wNumberOfOnes = CalculateNumberofOnes(wConfigBytes);
		wNumberOfOnes = (16 - wNumberOfOnes);
		wConfigBytes &= ~(1 << wNumberOfOnes);
		
		//Update The OTP buffer
		abyBuffer[0] = (uint8_t)((wConfigBytes & 0xFF00) >> 8); //MSB
		abyBuffer[1] = (uint8_t)(wConfigBytes & 0x00FF); //LSB
	}
	else
	{
		wConfigBytes = ((abyBuffer[0] & 0x7F) << 8) |(abyBuffer[1]);
		//Calculate number of configuration present in OTP
		wNumberOfOnes = CalculateNumberofOnes(wConfigBytes);
		//Set the BitMask 
		wConfigBytes = wConfigBytes | (1 << wNumberOfOnes);

		//Update the OTP buffer for indicating programming count is incremented by one.
		//First two bytes will represent the number of times the OTP is programmed. 
		abyBuffer[0] = (uint8_t)((wConfigBytes & 0x7F00) >> 8); //MSB
		abyBuffer[1] = ((uint8_t)(wConfigBytes & 0x00FF)); //LSB
	}

	
	//This is the logic for finding the OTP configuartion record update and data update.
	//Start from lowest index
	//By deafult, Data starts at 2 if no header found and record header will point end 
	//of otp minus the last configuarion data(2048-8).
	uint16_t gwOTPDataOffset = OTP_DATA_START_ADDRESS;
	uint16_t gwOTPHdrOffset = (1024 * 8) - sizeof(OTP_CFG_CHECKSUM_A1);
	uint16_t wTmpOTPDataOffset =0, wTmpLenght=0;
	OTP_CFG_CHECKSUM_A1 *pstChecksumA1 = NULL;

	pstChecksumA1 = (OTP_CFG_CHECKSUM_A1 *) &abyBuffer[gwOTPHdrOffset];

	wTmpOTPDataOffset = BIG_ENDIAN_WORD (pstChecksumA1->otpCfgChecksum.wCfgStartOffset);
	wTmpLenght = BIG_ENDIAN_WORD (pstChecksumA1->otpCfgChecksum.wCfgLength);
	
	while (('I' == pstChecksumA1->abySignature [0]) && \
			('D' == pstChecksumA1->abySignature [1]) && \
			('X' == pstChecksumA1->abySignature [2]))
	{
		if ((wTmpOTPDataOffset > 0x0800) || \
			(wTmpLenght > 0x0800))
		{
			// Though signature matched, still the offset or the length field is
			// indicating OTP access more than 2K, which is invalid
			// Probably an invlid index record, where the random bytes matched "IDX" pattern.
			DEBUGPRINT("Trying to access more than 2k OTP memory\n");
			return bRet;
		}

		// Update the data offset as valid header is found
		gwOTPDataOffset = (wTmpOTPDataOffset + wTmpLenght);

		// Move to next header
		pstChecksumA1 --;
		gwOTPHdrOffset-=sizeof(OTP_CFG_CHECKSUM_A1);
		
		wTmpOTPDataOffset = BIG_ENDIAN_WORD (pstChecksumA1->otpCfgChecksum.wCfgStartOffset);
		wTmpLenght = BIG_ENDIAN_WORD (pstChecksumA1->otpCfgChecksum.wCfgLength);
	}
	uint16_t wTotalIndexSize = ((1024 * 8) - gwOTPHdrOffset);

	if(wDataLength >= (unsigned int)((1024 * 8) - gwOTPDataOffset - wTotalIndexSize))
	{
		DEBUGPRINT("Error: No more free space available for programming OTP\n");
		return bRet;
	}
	//////////////////////////////////////////////
	// Update the OTP buffer for indicating programming count is incremented by one	
	bRet = Write_OTP(DevID, 0, abyBuffer, 2);
	if(bRet < 0)
	{
		DEBUGPRINT("Failed to write OTP \n");
		return bRet;
	}
	//////////////////////////////////////////////
	// Update the otp data with new cfg block
	bRet = Write_OTP(DevID, gwOTPDataOffset, pbyBuffer, wDataLength);
	if(bRet < 0)
	{
		DEBUGPRINT ("Failed to write OTP \n");
		return bRet;
	}
	//For comparing after programming.
	memcpy (&abyBuffer[gwOTPDataOffset], pbyBuffer, wDataLength);

	uint8_t byChecksum =0 ;
	OTP_CFG_CHECKSUM_A1 stChecksum;

	// Calculate the checksum
	for (int i = 0; i < wDataLength; i++)
	{
		byChecksum ^= pbyBuffer [i];
	}
	//OTP_CFG_CHECKSUM_A1 stChecksum;
	stChecksum.abySignature [0] = 'I';
	stChecksum.abySignature [1] = 'D';
	stChecksum.abySignature [2] = 'X';
	
	stChecksum.otpCfgChecksum.wCfgStartOffset = BIG_ENDIAN_WORD (gwOTPDataOffset);
	stChecksum.otpCfgChecksum.wCfgLength = BIG_ENDIAN_WORD (wDataLength);
	stChecksum.otpCfgChecksum.abyXORChecksum = byChecksum;
	
	//For comparing after programming.
	memcpy (&abyBuffer[gwOTPHdrOffset], &stChecksum, sizeof (OTP_CFG_CHECKSUM_A1));
		
	bRet = Write_OTP(DevID, gwOTPHdrOffset, (uint8_t *)&stChecksum, sizeof (OTP_CFG_CHECKSUM_A1));
	if(bRet < 0)
	{
		DEBUGPRINT("Failed to write OTP \n");
		return bRet;
	}
	sleep (2);
		
	//Verify OTP
	uint8_t abyVerifyBuffer[1024 * 8];
	bRet = Read_OTP(DevID, 0, abyVerifyBuffer, (1024 * 8));
	if(bRet < 0)
	{
		DEBUGPRINT("Failed to Read Config Memory \n");
		return bRet;
	}
	if(0 == memcmp(abyVerifyBuffer, abyBuffer, (1024 * 8)))
	{
		printf("OTP wrote successfully\n");
		writeBinfile("actual_otp_data.bin",  abyBuffer, (1024 * 8));
		bRet = TRUE;
	}
	else
	{
		printf("Mismatch in OTP read data\n");
		writeBinfile("expected_otp_data.bin",  abyBuffer, (1024 * 8));
		writeBinfile("actual_otp_data.bin",  abyVerifyBuffer, (1024 * 8));
	}
	//Reset the device.
	uint8_t byData = 0;
	xdata_read(DevID, 0x804, &byData, 1);

	byData|= 0x04;
	xdata_write(DevID, 0x804, &byData, 1);

	byData = 0x40;
	xdata_write(DevID, 0x80A, &byData, 1);
	
	return bRet;
}
/*----------------------- Helper functions -----------------------------------*/
static int usb_get_hubs(PHINFO pHubInfoList) 
{
	int cnt = 0, hubcnt = 0, i = 0, error=0;
	libusb_device **devs;
	libusb_device_descriptor desc;
	libusb_device_handle *handle;
	PHINFO pHubListHead = pHubInfoList;	// Pointer to head of the list
	
	error = libusb_init(&ctx);
	if(error < 0)
	{
		DEBUGPRINT("MCHP_Error_LibUSBAPI_Fail: Initialization LibUSB failed\n");
		return -1;
	}

	cnt = (int)(libusb_get_device_list(ctx, &devs));
	if(cnt < 0) 
	{
		DEBUGPRINT("Failed to get the device list \n");
		return -1;
	}


	for (i = 0; i < cnt; i++) 
	{
		int error = 0;
		int value = 0;

		libusb_device *device = devs[i];
		
		error = libusb_get_device_descriptor(device, &desc);
		if(error != 0)
		{
			DEBUGPRINT("LIBUSB_ERROR: Failed to retrieve device descriptor for device[%d] \n", i);
		}


		if((error ==  0) && (desc.bDeviceClass == LIBUSB_CLASS_HUB)) 
		{
			uint8_t hub_desc[ 7 /* base descriptor */
							+ 2 /* bitmasks */ * HUB_STATUS_BYTELEN];		  	


		  	error = libusb_open(device, &handle);
			if(error < 0) 
			{
				DEBUGPRINT("Cannot open device[%d] \t", i);
				switch(error)
				{
					case LIBUSB_ERROR_NO_MEM:
						DEBUGPRINT("LIBUSB_ERROR_NO_MEM \n");
					break;
					case LIBUSB_ERROR_ACCESS:
						DEBUGPRINT("LIBUSB_ERROR_ACCESS \n");
					break;
					case LIBUSB_ERROR_NO_DEVICE:
						DEBUGPRINT("LIBUSB_ERROR_NO_DEVICE \n");
					break;
					default:
						DEBUGPRINT("UNKNOWN_LIBUSB_ERROR \n");
					break;			
				}
				continue;
			}
		  
		 	memset(hub_desc, 0, 9);

			if(desc.bcdUSB == 0x0300)
			{
				value = 0x2A;
			}
		 	else
			{
		  		value = 0x29;
			}

			error = libusb_control_transfer(handle, 
											LIBUSB_ENDPOINT_IN | LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_DEVICE,
											LIBUSB_REQUEST_GET_DESCRIPTOR, 
											value << 8, 0, hub_desc, sizeof hub_desc, CTRL_TIMEOUT
											);

		  	if(error < 0) 
			{
				DEBUGPRINT("libusb_control_transfer device[%d]: \t", i);
				switch(error)
				{
					case LIBUSB_ERROR_TIMEOUT:
						DEBUGPRINT("LIBUSB_ERROR_TIMEOUT \n");
					break;
					case LIBUSB_ERROR_PIPE:
						DEBUGPRINT("LIBUSB_ERROR_PIPE \n");
					break;
					case LIBUSB_ERROR_NO_DEVICE:
						DEBUGPRINT("LIBUSB_ERROR_NO_DEVICE \n");
					break;
					default:
						DEBUGPRINT("UNKNOWN_LIBUSB_ERROR \n");
					break;			
				}
				continue;
			}

			pHubInfoList->port_max = libusb_get_port_numbers(device, pHubInfoList->port_list, 7);
			
		  	if(pHubInfoList->port_max <= 0) 
			{
				continue;
			}

			pHubInfoList->byPorts	= hub_desc[3];
			libusb_close(handle);

			pHubInfoList->wVID	 	= desc.idVendor;
			pHubInfoList->wPID 		= desc.idProduct;
			
			pHubInfoList++;
			hubcnt++;
		}
	}

	libusb_free_device_list(devs, 1);

	qsort(pHubListHead, hubcnt, sizeof(HINFO), compare_hubs);

	return hubcnt;
}

static int compare_hubs(const void *p1, const void *p2) 
{
	PHINFO pHub1, pHub2;

	pHub1 = (PHINFO) p1;
	pHub2 = (PHINFO) p2;


	if((VID_MICROCHIP == pHub1->wVID) && (VID_MICROCHIP == pHub2->wVID)) 
	{
		return 0; 	//Both Microchip hubs
	} 
	else if (VID_MICROCHIP == pHub1->wVID) 
	{
		return -1;	//Hub 1 is MCHP
	}
	else if (VID_MICROCHIP == pHub2->wVID) 
	{
		return 1;  //Hub 2 is MCHP
	}

	return 0;
}

static int usb_open_HCE_device(uint8_t hub_index) 
{
	libusb_device_handle *handle= NULL;
	libusb_device **devices;
	libusb_device *dev;
	libusb_device_descriptor desc;

	int dRetval = 0;
	ssize_t devCnt = 0, port_cnt = 0;
	ssize_t i = 0;
	uint8_t port_list[7];

	devCnt = libusb_get_device_list(ctx, &devices);
	if(devCnt < 0)
	{
		DEBUGPRINT("Enumeration failed \n");
		return -1;
	}


	for (i = 0; i < devCnt; i++) 
	{
		dev = devices[i];

		dRetval = libusb_get_device_descriptor(dev, &desc);
		if(dRetval < 0)
		{
			DEBUGPRINT("Cannot get the device descriptor \n");
			libusb_free_device_list(devices, 1);
			return -1;
		}

		if(PID_HCE_DEVICE == desc.idProduct)
		{
			dRetval = libusb_open(dev, &handle);
			if(dRetval < 0)
			{
				DEBUGPRINT("HCE Device open failed \n");
				return -1;
			}

			port_cnt = libusb_get_port_numbers(dev, port_list, 7);
			if(port_cnt <= 1) 
			{
				DEBUGPRINT("Retrieving port numbers failed \n");
				break;
			}

			//Match with the hub port list
			for(i = 0; i < gasHubInfo[hub_index].port_max; i++)
			{
				if(gasHubInfo[hub_index].port_list[i] != port_list[i]) 
				{
					DEBUGPRINT("Hub port match failed \n");
					dRetval = -1;
					break;
				}
			}
			
			if(dRetval == -1)
			{
				break;
			}

			printf("Enabled VID:PID = %04x:%04x ", desc.idVendor, desc.idProduct);
			for(i = 0; i < port_cnt; i++)
			{
				printf(":%d", (unsigned int)(port_list[i]));
			}
			printf("\n");
		

			if(libusb_kernel_driver_active(handle, 0) == 1)
			{
				//DEBUGPRINT("Kernel has attached a driver, detaching it \n");
				if(libusb_detach_kernel_driver(handle, 0) != 0)
				{
					DEBUGPRINT("Cannot detach kerenl driver. USB device may not respond \n");
					break;
				}
			}

			dRetval = libusb_claim_interface(handle, 0);

			if(dRetval < 0)
			{
				DEBUGPRINT("cannot claim intterface \n");
				dRetval = -1;
				break;
			}

			gasHubInfo[hub_index].dev = devices[i];
			gasHubInfo[hub_index].handle = handle;
			gasHubInfo[hub_index].byHubIndex = hub_index;

			return dRetval;

		}
	}
    if(handle)
    {
        libusb_close(handle);
    
    }

	
	
	libusb_free_device_list(devices, 1);
	return -1;
}

int usb_enable_HCE_device(uint8_t hub_index) 
{
	libusb_device_handle *handle;
	libusb_device **devices;
	libusb_device *dev;
	libusb_device_descriptor desc;

	int dRetval = 0;
	ssize_t devCnt = 0;
	ssize_t i = 0;

	devCnt = libusb_get_device_list(ctx, &devices);
	if(devCnt <= 0)
	{
		DEBUGPRINT("Enumeration failed \n");
		return -1;
	}

	for (i = 0; i < devCnt; i++) 
	{
		dev = devices[i];

		dRetval = libusb_get_device_descriptor(dev, &desc);
		if(dRetval < 0)
		{
			DEBUGPRINT("Cannot get the device descriptor \n");
			libusb_free_device_list(devices, 1);
			return -1;
		}

		if(MICROCHIP_HUB_VID == desc.idVendor)
		{
			dRetval = libusb_open(dev, &handle);
			if(dRetval < 0)
			{
				DEBUGPRINT("HCE Device open failed \n");
				return -1;
			}

			if(libusb_kernel_driver_active(handle, 0) == 1)
			{
				
				if(libusb_detach_kernel_driver(handle, 0) != 0)
				{
					DEBUGPRINT("Cannot detach kerenl driver. USB device may not respond \n");
					libusb_close(handle);
					break;
				}
			}

			/*dRetval = libusb_claim_interface(handle, 0);

			if(dRetval < 0)
			{
				DEBUGPRINT("cannot claim intterface \n");
				libusb_close(handle);
				break;
			}*/

			uint16_t val = 0x0001;
			dRetval = usb_send_vsm_command(handle,(uint8_t*)&val);
			if(dRetval < 0)
			{
				DEBUGPRINT("HCE Device: VSM command 0x0001 failed \n");
				libusb_close(handle);
				break;
			}

			val = 0x0201;
			dRetval = usb_send_vsm_command(handle,(uint8_t*)&val);
			if(dRetval < 0)
			{
				DEBUGPRINT("HCE Device: VSM command 0x0201 failed \n");
			}
			sleep(2);

			libusb_close(handle);
			libusb_free_device_list(devices, 1);
			return dRetval;
		}
	}

		
		
	libusb_free_device_list(devices, 1);
	return -1;
}

int  usb_send_vsm_command(struct libusb_device_handle *handle, uint8_t * byValue)
{
	int rc = 0;

	rc = libusb_control_transfer(	handle, 
					0x40,
					0x02, 
					0, 
					0, 
					byValue, 
					2, 
					CTRL_TIMEOUT
				);
	return rc;
	
}
int Read_OTP(HANDLE handle, uint16_t wAddress, uint8_t *data, uint16_t num_bytes)
{
	int bRetVal = FALSE;
	WORD wReadLength,wTemp;
	USB_CTL_PKT UsbCtlPkt;
	
	if(num_bytes < MAX_OTP_READ_SIZE)
	{
		UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[handle].handle;
		UsbCtlPkt.byRequest = 0x01;
		UsbCtlPkt.wValue 	= wAddress;
		UsbCtlPkt.wIndex 	= 0;
		UsbCtlPkt.byBuffer 	= data;
		UsbCtlPkt.wLength 	= num_bytes;

		bRetVal = usb_HCE_read_data (&UsbCtlPkt);
	}
	else
	{
		wReadLength = MAX_OTP_READ_SIZE;
		wTemp = num_bytes;
		while(wTemp)
		{	
			UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[handle].handle;
			UsbCtlPkt.byRequest = 0x01;
			UsbCtlPkt.wValue 	= wAddress;
			UsbCtlPkt.wIndex 	= 0;
			UsbCtlPkt.byBuffer 	= data;
			UsbCtlPkt.wLength 	= wReadLength;

			bRetVal = usb_HCE_read_data (&UsbCtlPkt);
			if(bRetVal< 0)
			{
				break;
			}
			wAddress = wAddress + MAX_OTP_READ_SIZE;
			data += wReadLength;
			wTemp = wTemp - wReadLength;
			if(wTemp < MAX_OTP_READ_SIZE)
			{
				wReadLength = wTemp;
			} 
		}	
	}
	if(bRetVal< 0)
	{
		DEBUGPRINT("Read OTP failed %d\n",bRetVal);
		return bRetVal;
	}
	return bRetVal;
}
int Write_OTP(HANDLE handle, uint16_t wAddress, uint8_t *data, uint16_t num_bytes)
{
	int bRetVal = FALSE;
	USB_CTL_PKT UsbCtlPkt;

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[handle].handle;
	UsbCtlPkt.byRequest = 0x00;
	UsbCtlPkt.wValue 	= wAddress;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= data;
	UsbCtlPkt.wLength 	= num_bytes;

	bRetVal = usb_HCE_write_data (&UsbCtlPkt);
	if(bRetVal< 0)
	{
		DEBUGPRINT("Execute write OTP command failed %d\n",bRetVal);
		return bRetVal;
	}
	return bRetVal;
}
int xdata_read(HANDLE handle, uint16_t wAddress, uint8_t *data, uint8_t num_bytes)
{
	int bRetVal = FALSE;
	USB_CTL_PKT UsbCtlPkt;

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[handle].handle;
	UsbCtlPkt.byRequest 	= 0x04;
	UsbCtlPkt.wValue 	= wAddress;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= data;
	UsbCtlPkt.wLength 	= num_bytes;

	bRetVal = usb_HCE_read_data (&UsbCtlPkt);
	return bRetVal;
}

int xdata_write(HANDLE handle, uint16_t wAddress, uint8_t *data, uint8_t num_bytes)
{
	int bRetVal = FALSE;
	USB_CTL_PKT UsbCtlPkt;

	UsbCtlPkt.handle 	= (libusb_device_handle*)gasHubInfo[handle].handle;
	UsbCtlPkt.byRequest 	= 0x03;
	UsbCtlPkt.wValue 	= wAddress;
	UsbCtlPkt.wIndex 	= 0;
	UsbCtlPkt.byBuffer 	= data;
	UsbCtlPkt.wLength 	= num_bytes;

	bRetVal = usb_HCE_write_data (&UsbCtlPkt);
	return bRetVal;
}

bool UsbSetBitXdata(int hub_index,WORD wXDataAddress,BYTE byBitToSet)
{
	BYTE byData;
	bool bRet = false;
	do
	{
		bRet= MchpUsbRegisterRead ( hub_index, wXDataAddress, 1, &byData );
		if (!bRet)
		{
			break;
		}

		byData |= byBitToSet;
		bRet= MchpUsbRegisterWrite( hub_index, wXDataAddress, 1, &byData) ;
		if (!bRet)
		{
			break;
		}

	} while (FALSE);

	return bRet;
}

bool UsbClearBitXdata(int hub_index,WORD wXDataAddress,BYTE byBitToClear)
{
	BYTE byData;
	bool bRet = false;
	do
	{
		bRet= MchpUsbRegisterRead ( hub_index, wXDataAddress, 1, &byData );
		if (!bRet)
		{
			break;
		}

		byData &=~ byBitToClear;

		bRet= MchpUsbRegisterWrite( hub_index, wXDataAddress, 1, &byData) ;
		if (!bRet)
		{
			break;
		}

	} while (FALSE);

	return bRet;
}
int USB_I2C_Transfer(int hub_index,BOOL byDir,uint8_t byAddr, uint8_t *pbyBuffer, uint16_t wLength , uint32_t *wdActualLength)
{
	BYTE byFlags, byCmd;
	int bRet = FALSE;

	WORD wAddress,temp = 0;

	do
	{
		if (wLength > 512)
		{
			break;
		}
		if (byDir)// I2c Read
		{
			byFlags = SEND_NACK | SEND_START |SEND_STOP;
		}
		else
		{
			byFlags = SEND_START |SEND_STOP;
		}
		byAddr = byAddr << 1;

		if (byDir)// I2c Read
		{
			byCmd = I2C_READ_CMD;
			byAddr |= I2C_READ_BIT;
			temp = byAddr;
			temp |= ((WORD)byFlags) << 8;

			wAddress = temp;
			bRet = libusb_control_transfer((libusb_device_handle*)gasHubInfo[hub_index].handle,0xC1,byCmd,wAddress,0,&pbyBuffer[0],wLength,500);
			if(bRet <0)
			{
				DEBUGPRINT("I2C Read Failed \n");	
			}
			else
			{
				DEBUGPRINT("I2C Read Success \n");	
			}
		}	
		else
		{
			byCmd = I2C_WRITE_CMD;
			temp = byAddr;
			temp |= ((WORD)byFlags) << 8;

			wAddress = temp;
			bRet = libusb_control_transfer((libusb_device_handle*)gasHubInfo[hub_index].handle,0x41,byCmd,wAddress,0,&pbyBuffer[0],wLength,500);
			if(bRet <0)
			{
				DEBUGPRINT("I2C Write Failed \n");	
			}
			else
			{
				DEBUGPRINT("I2C Write Success \n");	
			}	
		}
	}while(FALSE);
	return bRet;
}
BOOL Gen_I2C_Transfer (int hub_index, BOOL bDirection, BYTE* pbyBuffer, WORD wDataLen, BYTE bySlaveAddress,BOOL bStart,BOOL bStop,BOOL bNack)
{
	BYTE byFlags;
	WORD wAddress;
	BYTE byCmd, byRequestType;
	int rc = FALSE;
	do
	{
		if (wDataLen > 512)
		{
			DEBUGPRINT("Invalid Data length \n");
			break;
		}
		if (bStart)
		{
			byFlags |= I2CFL_SEND_START;
		}
		if (bStop)
		{
			byFlags |= I2CFL_SEND_STOP;
		}

		if (bNack)
		{
			byFlags |= I2CFL_SEND_NACK;
		}
		bySlaveAddress = bySlaveAddress << 1;
		if (bDirection)	// From device to USB host
		{
			bySlaveAddress	= bySlaveAddress | I2C_READ_BIT;
		}
		wAddress = MAKEWORD (bySlaveAddress, byFlags);
		if (bDirection)	// From device to USB host
		{
			byRequestType = 0xc1;
			byCmd		= CMD_I2C_READ;
		}
		else	// From USB to device
		{
			byRequestType = 0x41;
			byCmd		= CMD_I2C_WRITE;
		}
		rc = libusb_control_transfer((libusb_device_handle*)gasHubInfo[hub_index].handle,byRequestType,byCmd,wAddress,0,
										pbyBuffer,wDataLen,CTRL_TIMEOUT);
		if(rc < 0)
		{
			DEBUGPRINT("I2C Transfer Failed \n");
			return FALSE;
		}
		
	}while(FALSE);
	return TRUE;
}
unsigned int CalculateNumberofOnes(unsigned int UINTVar)
{
	unsigned int N0OfOnes = 0;
	do
	{
		if(0x0000 == UINTVar) // variable if zero then return 0
			break;
		// Now counts 1's
		while(UINTVar)
		{
			N0OfOnes++;
			UINTVar &= (UINTVar -1);
		}
	}while(false);

	return N0OfOnes;
}


