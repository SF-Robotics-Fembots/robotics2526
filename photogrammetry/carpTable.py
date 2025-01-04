from tkinter import *
from tkinter import ttk

ws=Tk()

ws.title('CarpTable')
ws.geometry('800x500')

set = ttk.Treeview(ws)
set.pack()

Input_frame = Frame(ws)
Input_frame.pack()

#set['columns']= ('Region_1', 'Region_2','Region_3', 'Region_4', 'Region_5')
set['columns']= ('Year', 'Region_1', 'Region_2','Region_3', 'Region_4', 'Region_5')
set.column("#0", width=0,  stretch=NO)
set.column("Year",anchor=CENTER, width=70)
set.column("Region_1",anchor=CENTER, width=70)
set.column("Region_2",anchor=CENTER, width=70)
set.column("Region_3",anchor=CENTER, width=70)
set.column("Region_4",anchor=CENTER, width=70)
set.column("Region_5",anchor=CENTER, width=70)

set.heading("#0",text="",anchor=CENTER)
set.heading("Year",text="Year",anchor=CENTER)
set.heading("Region_1",text="Region 1",anchor=CENTER)
set.heading("Region_2",text="Region 2",anchor=CENTER)
set.heading("Region_3",text="Region 3",anchor=CENTER)
set.heading("Region_4",text="Region 4",anchor=CENTER)
set.heading("Region_5",text="Region 5",anchor=CENTER)

#data
# data  = [
#     [],
#     [],
#     [],
#     [],
#     []
# ]

global count
count=0

# for i in years:
    
#     for j in i:
#         set.insert(parent='',index='end',iid = count,text='',values=(j[i[0]],i[i[1]],i[i[2]],i[i[3]],i[i[4]],i[i[5]],i[i[6]],i[i[7]],i[i[8]]))
       
#     count += 1

year = Label(Input_frame,text="Year")
year.grid(row=0,column=0)

region_1 = Label(Input_frame,text="Region 1")
region_1.grid(row=0,column=1)

region_2= Label(Input_frame,text="Region 2")
region_2.grid(row=0,column=2)

region_3 = Label(Input_frame,text="Region 3")
region_3.grid(row=0,column=3)

region_4 = Label(Input_frame,text="Region 4")
region_4.grid(row=0,column=4)

region_5= Label(Input_frame,text="Region 5")
region_5.grid(row=0,column=5)


year_entry = Entry(Input_frame)
year_entry.grid(row=1,column=0)

region1_entry = Entry(Input_frame)
region1_entry.grid(row=1,column=1)

region2_entry = Entry(Input_frame)
region2_entry.grid(row=1,column=2)

region3_entry = Entry(Input_frame)
region3_entry.grid(row=1,column=3)

region4_entry = Entry(Input_frame)
region4_entry.grid(row=1,column=4)

region5_entry = Entry(Input_frame)
region5_entry.grid(row=1,column=5)


def input_record():
    
    global count
    
    set.insert(parent='',index='end',iid = count,text='',values=(year_entry.get(),region1_entry.get(),region2_entry.get(),region3_entry.get(),region4_entry.get(),region5_entry.get()))
    count += 1

    year_entry.delete(0,END)
    region1_entry.delete(0,END)
    region2_entry.delete(0,END)
    region3_entry.delete(0,END)
    region4_entry.delete(0,END)
    region5_entry.delete(0,END)
     
#button
Input_button = Button(ws,text = "Input Record",command= input_record)

Input_button.pack()

ws.mainloop()