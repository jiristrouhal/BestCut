import tkinter as tk
import pick_and_cut as pc
from typing import List
import cz
import hints


INPUT_BACKUP_FILE = "_last_.out"


window = tk.Tk()
window.geometry("800x600")
window.title("BestCut")
window.iconbitmap(bitmap="./icon.ico")


input_frame = tk.Frame(window)
input_frame.pack(side=tk.TOP,expand=1)
controls_frame = tk.Frame(window)
controls_frame.pack(side=tk.TOP)
save_frame = tk.Frame(window)
save_frame.pack(side=tk.BOTTOM,expand=1)
output_frame = tk.Frame(window)
output_frame.pack(side=tk.BOTTOM,expand=2)


from typing import List
import re
ITEM_DELIM = ";"
def is_int_list(src:str)->bool:
	if src.strip()=="": return True
	if src[0]==";": return False
	if re.match(r";[\D]*;",src): return False 

	if src[0]==ITEM_DELIM: src=src[1:]

	for item in src.split(ITEM_DELIM):
		item = item.strip()
		if not (re.fullmatch(r"\d+",item) or item==""):
			return False
		elif item!='' and item[0]=='0':
			return False
	return True


def restrict_characters_in_stock_entry(src:str)->bool:
	is_valid = True
	all_valid_stock_items = True
	if src.strip()=="": return True
	if src[0]==";": return False
	if re.match(r";[\D]*x?;",src): return False 

	if src[-1]==ITEM_DELIM: src=src[:-1]

	for item in src.split(ITEM_DELIM):
		item = item.strip()
		if not (re.fullmatch(r"[(),\d]+",item) or item==""):
			is_valid = False
			break
		elif not (re.fullmatch(r"\([\d]+[\s]*,[\s]*[\d]+\)",item)  or item==""):
			all_valid_stock_items = False
		elif re.match(r",[\w]\)*",item):
			all_valid_stock_items = False
		
	if not all_valid_stock_items: stock_input.config(foreground="red")
	else: stock_input.config(foreground="black")
	return is_valid


def auto_format_spaced_between_lengths(event:tk.Event)->None:
	src = lengths_input.get()
	for digit in range(10): src=src.replace(f"{ITEM_DELIM}{digit}",f"{ITEM_DELIM} {digit}")
	src= src.replace("  "," ")
	lengths_input.delete(0,tk.END)
	lengths_input.insert(0,src)


def auto_add_space_before_left_parenthesis(event:tk.Event)->None:
	src = lengths_input.get()
	src=src.replace(f"{ITEM_DELIM}\(",f"{ITEM_DELIM} \(")
	lengths_input.delete(0,tk.END)
	lengths_input.insert(0,src)


priority_frame = tk.Frame(input_frame)
priority_frame.pack(side=tk.BOTTOM)
priority_label = tk.Label(priority_frame, text=cz.WHAT_TO_MINIMIZE)
priority_label.pack(side=tk.LEFT)


priority_var = tk.StringVar(priority_frame, pc.pickstock.COST)
priority_button_both = tk.Radiobutton(priority_frame, text=cz.BOTH, variable=priority_var, value=pc.pickstock.COST_AND_COUNT)
priority_button_both.pack(side=tk.RIGHT)
priority_button_items = tk.Radiobutton(priority_frame, text=cz.BOUGHT_STOCK_ITEMS, variable=priority_var, value=pc.pickstock.COUNT)
priority_button_items.pack(side=tk.RIGHT)
priority_button_cost = tk.Radiobutton(priority_frame, text=cz.COST, variable=priority_var, value=pc.pickstock.COST)
priority_button_cost.pack(side=tk.RIGHT)


vcmd_lengths = (window.register(is_int_list))
vcmd_stock = (window.register(restrict_characters_in_stock_entry))
lengths_input = tk.Entry(input_frame,width=100,validate="key",validatecommand=(vcmd_lengths,'%P'))
lengths_input.bind("<FocusOut>",auto_format_spaced_between_lengths)
lengths_input.pack()
stock_input = tk.Entry(input_frame,width=100,validate="key",validatecommand=(vcmd_stock,'%P'))
stock_input.pack()
stock_input.bind("<FocusOut>",auto_add_space_before_left_parenthesis)


hints.createToolTip(lengths_input,text=cz.LENGTH_INPUT_HELP)
hints.createToolTip(stock_input,text=cz.STOCK_INPUT_HELP)


order_output = tk.Text(output_frame,width=30)
order_output.pack(side=tk.LEFT,expand=1)
combined_lengths_output = tk.Text(output_frame,width=30)
combined_lengths_output.pack(side=tk.RIGHT,expand=1)
cutted_stock_output = tk.Text(output_frame,width=30)
cutted_stock_output.pack(side=tk.RIGHT,expand=1)


def __underline(text:str)->str:
	text += "\n"+"–"*len(text)
	return text


def __read_lengths_input()->List[int]:
	lengths_str:List[str] = lengths_input.get().split(ITEM_DELIM)
	lengths:List[int] = list()
	for li in lengths_str: 
		li = li.strip()
		if li=='': continue
		lengths.append(int(li))
	return lengths


def __read_stock_input()->List[pc.Stock]:
	stock_str:List[str] = stock_input.get().split(ITEM_DELIM)
	if len(stock_str)==0: return []
	stock:List[pc.Stock] = list()
	for s in stock_str:
		if s.strip()=='': continue
		s=s.replace("(","").replace(")","").strip()
		if s.count(",") != 1: return []
		length, price = tuple(s.split(","))
		stock.append(pc.Stock(int(length),int(price)))
	return stock


def __redraw_order(order:pc.Ordered_Stock)->None:
	order_str = __underline(cz.ORDER)+"\n"
	order_str += cz.TOTAL_COST+":"+f" {order.total_price}\n\n" + cz.ITEMS+":\n"
	for length,count in order.items.items():
		order_str += f"\t{length:5} ...\t{count:3} {cz.PIECES}\n"
	order_output.delete("1.0",tk.END)
	order_output.insert(tk.END,order_str)


def __redraw_cutted_stock(stock:List[pc.Cutted_Stock])->None:
	stock_str = __underline(cz.HOW_TO_CUT_STOCK)+"\n"
	if stock:
		for s in stock:
			stock_str += f"{s.original_length:4} → "
			for piece in s.pieces[:-1]:
				stock_str += f"{piece}, "
			stock_str += f"{s.pieces[-1]}\n"

	cutted_stock_output.delete("1.0",tk.END)
	cutted_stock_output.insert(tk.END,stock_str)


def __redraw_combined_lengths(lengths:List[pc.Combined_Length])->None:
	lengths_str = __underline(cz.HOW_TO_COMBINE_LENGTHS)+"\n"
	if lengths:
		for l in lengths:
			lengths_str += f"{l.length:4} ← "
			for piece in l.pieces[:-1]:
				lengths_str += f"{piece}, "
			if len(l.pieces)>0:
				lengths_str += f"{l.pieces[-1]}\n"
	combined_lengths_output.delete("1.0",tk.END)
	combined_lengths_output.insert(tk.END,lengths_str)


def store_used()->None:
	with open(INPUT_BACKUP_FILE,'w') as fw:
		lengths_input_line = lengths_input.get()+'\n'
		stock_input_line = stock_input.get()
		fw.writelines([lengths_input_line,stock_input_line])
		fw.close()


def calculate()->None:
	lengths = __read_lengths_input()
	stock = __read_stock_input()
	store_used()
	if not (lengths and stock): 
		__redraw_order(pc.Ordered_Stock(0, {}))
		__redraw_cutted_stock([])
		__redraw_combined_lengths([])
	else:
		result = pickandcut_by_priority(lengths,stock)
		__redraw_order(result.order)
		__redraw_cutted_stock(result.cutted_stock)
		__redraw_combined_lengths(result.combined_lengths)


def pickandcut_by_priority(lengths:List[int],stock:List[pc.Stock]):
	global priority_var
	match priority_var.get():
		case pc.pickstock.COST:
			return pc.pickandcut(lengths,stock,'cost')
		case pc.pickstock.COUNT:
			return pc.pickandcut(lengths,stock,'count')
		case pc.pickstock.COST_AND_COUNT:
			return pc.pickandcut(lengths,stock,'cost and count')


calculate_button = tk.Button(controls_frame,text=cz.CALCULATE,command=calculate)
calculate_button.pack()


import datetime
import tkinter.filedialog as filedialog
import os.path
last_dir = '.'
initial_file_name = cz.RESULTS
def __save_printed_output_to_file()->None:
	global last_dir
	order = order_output.get("1.0",tk.END)
	cutted_stock = cutted_stock_output.get("1.0",tk.END)
	combined_lengths = combined_lengths_output.get("1.0",tk.END)
	total = (order+cutted_stock+combined_lengths).strip()
	if total=="":
		return
	now = str(datetime.datetime.now())
	now = now.replace(":","-")[:-7]
	filename = filedialog.asksaveasfilename(
		title=cz.SAVE_INTO,
		defaultextension='txt',
		filetypes=((cz.TEXT_FILE, "txt"),),
		initialdir=last_dir,
		initialfile=initial_file_name+' '+str(datetime.datetime.now()).replace(':','-')[:-7]
		)
	if filename!='': 
		last_dir = os.path.dirname(filename)
		with open(filename,"w") as f:
			f.write(order)
			f.write(cutted_stock)
			f.write(combined_lengths)
			f.close()


print_button = tk.Button(save_frame,text="Uložit",command=__save_printed_output_to_file)
print_button.pack(side=tk.BOTTOM)


import os.path

def load_on_start()->None:
	if not os.path.isfile(INPUT_BACKUP_FILE): return 
	with open(INPUT_BACKUP_FILE,'r') as fr:
		lengths = fr.readline().replace('\n','')
		stock = fr.readline().replace('\n','')
		if lengths!="": assert(lengths[-1]!='\n')
		if stock!="": assert(stock[-1]!='\n')
		lengths_input.insert(0,lengths)
		stock_input.insert(0,stock)
		fr.close()


window.after(50,load_on_start)
window.mainloop()