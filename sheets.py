import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from datetime import date

todate = date.today()
todate = todate.strftime("%d/%m/%Y")
print(todate)
roll = "15499021010"
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("your_google_sheet_service_account_creds.json", scope)

client = gspread.authorize(creds)

mscsheet = client.open("MScAttendance").sheet1
bbasheet = client.open("BBAAttendance").sheet1
bcasheet = client.open("BCAAttendance").sheet1
bmltsheet = client.open("BMLTAttendance").sheet1
sheet = mscsheet
def updateGoogleSheet(roll, department, classtime):
    global sheet
    datetime = todate+" "+classtime
    if department == "BBA" or department == "BHM":
        sheet = bbasheet
    elif department == "BCA":
        sheet = bcasheet
    elif department == "BSC-MLT":
        sheet = bmltsheet
    mainRow = sheet.row_values(1)
    rollCol = sheet.col_values(1)
    presentDate = len(mainRow)
    mainRowCount = len(mainRow)
    if mainRow[mainRowCount-1] != datetime:
        sheet.update_cell(1, mainRowCount+1, datetime)
        presentDate = mainRowCount + 1

    for i in range(0, len(rollCol)):
        if(roll == rollCol[i]):
            sheet.update_cell(i+1, presentDate, "p")


def inserIntoGoogleSheet(roll, name, department):
    global sheet
    if department == "BBA" or department == "BHM":
        sheet = bbasheet
    elif department == "BCA":
        sheet = bcasheet
    elif department == "BSC-MLT":
        sheet = bmltsheet
    rollCol = sheet.col_values(1)
    mainRowCount = len(rollCol)
    for i in range(0, mainRowCount):
        if(roll == rollCol[i]):
            return
    sheet.update_cell(mainRowCount+1,1,roll)
    sheet.update_cell(mainRowCount+1,2,name)
    return

def changeGoogleSheet(roll, name, prevDept, currDept):
    global sheet
    sheetTemp = mscsheet
    if prevDept == "BBA" or prevDept == "BHM":
        sheetTemp = bbasheet
    elif prevDept == "BCA":
        sheetTemp = bcasheet
    elif prevDept == "BSC-MLT":
        sheetTemp = bmltsheet
    else:
        sheetTemp = mscsheet

    if currDept == "BBA" or currDept == "BHM":
        sheet = bbasheet
    elif currDept == "BCA":
        sheet = bcasheet
    elif currDept == "BSC-MLT":
        sheet = bmltsheet
    
    rollCol = sheetTemp.col_values(1)
    mainRowCount = len(rollCol)
    for i in range(0, mainRowCount):
        if(roll == rollCol[i]):
            sheetTemp.delete_row(i+1)
            break
    rollCol = sheet.col_values(1)
    mainRowCount = len(rollCol)
    for i in range(0, mainRowCount):
        if(roll == rollCol[i]):
            return
    sheet.update_cell(mainRowCount+1,1,roll)
    sheet.update_cell(mainRowCount+1,2,name)


"""
data = sheet.get_all_records()

row = sheet.row_values(1)
rollCol = sheet.col_values(1)
presentDate = len(row)
#pprint(data)
print(row)

if row[len(row)-1] != todate:
    sheet.update_cell(1, len(row)+1, todate)
    presentDate = len(row) + 1

for i in range(0, len(rollCol)):
    if(roll == rollCol[i]):
        sheet.update_cell(i+1, presentDate, "p")
"""