from fpdf import FPDF
import datetime
import argparse

def say_hi():
    print(f"""
    -----------------------
    Welcome to Vesuvius 
    Version Alpha 001 
    -----------------------
    Today is {datetime.date.today()}

    """)

def tableColumns(df):
    for col in df.columns:
        yield col

def tableValues(df):
    for _,row in df.iterrows():
        yield row


def generate_report(df, output_pdf_path, kwargs):
    """
    A script that takes a dataframe and outputs the relevant data as a pdf
    """
    # Define relevant columns in df
    df_unfiltered = df # save a copy of the complete df
    df = df[['v_name', 'start_y', 'start_m', 'start_d', 'delta', 'lat', 'lon', 'sat_lats', 'sat_lons']]
    pdf = FPDF("P","mm","A4")
    pdf.add_page()
    def page_header():
        pdf.set_font('Arial',style='B', size=16)
        pdf.set_text_color(255)
        pdf.set_fill_color(230,130,0)
        pdf.cell(0, 10, 'Vesuvius Alpha', 0,1, align='C', fill=True)
        pdf.set_font('Arial',style='', size=10)
        pdf.set_text_color(0)
        pdf.cell(0, 8, 'A python project by Roberto Henríquez Perozo.',0,1)
        pdf.cell(0, 8, 'Data Analytics Bootcamp - IronHack Madrid.',0,1)
    
    # Generate landing page
    page_header()
    pdf.cell(0, 8, f'This report was generated on: {datetime.datetime.today()}',0,1)
    pdf.cell(0, 8, f"Requested date(YYYY-MM):   {kwargs['requested_year']}-{kwargs['requested_month']}",0,1)
    pdf.cell(0, 8, f'Available data: {df.shape[0]} rows and {df.shape[1]} columns.',0,1)
    
    pdf.cell(0, 8, f'Volcanoes with registered eruptions on requested date:',0,1)
    for v_name in df.v_name:
        pdf.cell(0, 8, f'     - {v_name}',0,1)



    pdf.cell(0, 8, f'{list(tableColumns(df))}',0,1)

    # PDFCONFIG.PY
    # Dictionaries for 2 font settings and 3 color settings
    # Usefull for changing settings without having to go through code.
    font_type_table_header = {"family":"Arial", "style":"B", "size":10}
    font_type_table_body = {"family":"Arial", "style":"", "size":8}
    black = (0,-1,-1)
    green = (10,188,87)
    yellow = (250,239,133)


    #MAKEPRETTY.PY
    # Create an instance of `FPDF` to use it's methods
    # It is created outside of the function, because otherwise
    # it would generate a new object every time you called `fit_word`
    ver = FPDF()

    def fit_word(string,cell_w,font_type):
        string=str(string)
        ver.set_font(**font_type)
        width = ver.get_string_width(string)
        if ver.get_string_width(string)<cell_w:
            return string
        while ver.get_string_width(string)>=cell_w:
            string = string[:-1]
        string = string[:-3] + "..."
        return string


    # Define our cols and num_cols so cell width is calculated relatively
    # You can change the number of columns and it will adapt to fit
    # the whole page (190 mm = 210mm - 2 * 10mm)
    # 10mm is the default left and right margins
    cols = list(tableColumns(df))
    num_cols = len(cols)
    A4_width = 210
    l_margin = 10
    r_margin = 10
    useful_page_width = A4_width-l_margin-r_margin

    # Use font_type_table_header and font_type_table_body
    # to get font configuration from other file `config.py`
    # so it can be changed without going through code.
    # The same can be applied to color, etc.
    pdf.set_font(**font_type_table_header)
    pdf.set_draw_color(0)
    pdf.set_text_color(0)

    cell_width = useful_page_width/num_cols

    # Printing Header
    for col in cols:
        pdf.cell(cell_width,10,col.upper(),1,0,"C")
    # Add line break after printing whole line
    pdf.ln()

    # Printing rows
    pdf.set_font(**font_type_table_body)
    pdf.set_fill_color(255)
    for row in tableValues(df): 
        for val in row:
            pdf.cell(cell_width,10,fit_word(val,cell_width,font_type_table_body),1,0,"C",1)
        pdf.ln()


    def new_event_page(pandas_row):
        """
        This function will be once called for each existing event, to generate a correctly formatted response
        """
        pdf.add_page()
        page_header()

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, f"Volcano name:",0,1)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 8, f"  {pandas_row['v_name']}",0,1)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, f"Volcano coordinates:",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"  [lat:{pandas_row['lat']}, lon{pandas_row['lon']}]",0,1)


        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, f"First available satellite image:",0,1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"  {pandas_row['start_img']}",0,1)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, f"Total satellite images available: {pandas_row['start_img_available_in_api']}",0,1)
        

#        pdf.cell()
        pass
    
    """
    for i in range(len(df)):
        for e in df:
            pdf.cell(0,10,f'Volcano name: {df.iloc[i]}',0,1)
            #print(df.iloc[i])
    """

    for row in tableValues(df_unfiltered):
        #for val in row:
            new_event_page(row)
        


    pdf.output(output_pdf_path, 'F')
