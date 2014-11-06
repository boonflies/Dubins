# ----------------
# Change Log
# ----------------
# Date: Oct 07, 2014

# Modification:
#   1. excel_read function, changed the input excel file name to 'Target_Positions.xlsx'
# --------------------------------------------------------------------------------------


import xlsxwriter
import xlrd


def excel_write(x_UAV, y_UAV, z_UAV, UAV_heading, UAV_bearing, x_target, y_target, z_target,
    target_heading, target_bearing, distance, distance_obs, algorithm):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('Waypoints.xlsx')
    worksheet = workbook.add_worksheet()

    # Start from the first cell. Rows and colums are zero indexed.
    row = 2
    col = 0
    count = 1

    # Create a format to use in the cell
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'bg_color': 'green',
        'valign':'vcenter'})

    normal_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'})

    clear_format = workbook.add_format({
        'border': 0})

    # Create the outline for the content
    worksheet.merge_range('A1:A2', 't', merge_format)
    worksheet.merge_range('B1:F1', 'UAV', merge_format)
    worksheet.merge_range('G1:K1', 'Target', merge_format)
    worksheet.merge_range('L1:L2', 'Distance to Target', merge_format)
    worksheet.merge_range('M1:M2', 'Distance to Obstacle', merge_format)
    worksheet.merge_range('N1:N2', 'Algorithm Type', merge_format)
    worksheet.write(1, 1, 'x', normal_format, )
    worksheet.write(1, 2, 'y', normal_format)
    worksheet.write(1, 3, 'z', normal_format)
    worksheet.write(1, 4, 'heading', normal_format)
    worksheet.write(1, 5, 'bearing', normal_format)
    worksheet.write(1, 6, 'x', normal_format)
    worksheet.write(1, 7, 'y', normal_format)
    worksheet.write(1, 8, 'z', normal_format)
    worksheet.write(1, 9, 'heading', normal_format)
    worksheet.write(1, 10, 'bearing', normal_format)
    worksheet.write(2, 0, 'Initial', normal_format)


    # iterate over the data and write it out row by row
    for i in range(len(x_UAV)):
        worksheet.write(row + 1, 0, count, normal_format)
        try:
            worksheet.write(row, 1, x_UAV[i], normal_format)
            worksheet.write(row, 2, y_UAV[i], normal_format)
            worksheet.write(row, 3, z_UAV[i], normal_format)
            worksheet.write(row, 4, UAV_heading[i], normal_format)
            worksheet.write(row, 5, UAV_bearing[i], normal_format)

            worksheet.write(row, 6, x_target[i], normal_format)
            worksheet.write(row, 7, y_target[i], normal_format)
            worksheet.write(row, 8, z_target[i], normal_format)
            worksheet.write(row, 9, target_heading[i], normal_format)
            worksheet.write(row, 10, target_bearing[i], normal_format)
            worksheet.write(row, 11, distance[i], normal_format)
            worksheet.write(row, 12, distance_obs[i], normal_format)
            worksheet.write(row, 13, algorithm[i], normal_format)

        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message

        row += 1
        count += 1

    #tweaking code
    worksheet.write(row , 0, '', clear_format)
    worksheet.write(row - 1, 0, 'Final', normal_format)

    workbook.close()



def excel_read():
        workbook = xlrd.open_workbook('Target_Positions.xlsx')
        worksheet = workbook.sheet_by_name('Sheet1')
        row_start = 2   # start the row count from 1 as in excel
        row_end = len(worksheet.col_values(0))
        col_start = 2   # start the column count from 1

        Target = [[] for _ in range(row_end - 1)]
        entries_count = 0
        for j in range(row_start -1, row_end):
            for i in range(col_start - 1, 6):
                Target[entries_count].append(worksheet.cell(j,i).value)
            entries_count += 1


        return Target

