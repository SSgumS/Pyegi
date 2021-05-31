--[[
You might want to install pyonfx and pyyaml through cmd using:
pip install pyonfx
pip install pyyaml


]]--

script_name = "Pyegi"
script_description = "."
script_version = "0.0.1"
script_author = "."
script_namespace = "Pyegi"

--include('karaskel.lua')
local yaml = require 'Azarakhsh.yaml'

function main(sub,sel)
	local python_path = "C:/Python39/python.exe" --the path to your python.exe
	local sc_dir = "C:/Users/saman/AppData/Roaming/Aegisub/automation/autoload/PythonScripts/" --the path to the python scripts
	local dir_table = scandir(sc_dir)
	
	local ADD = aegisub.dialog.display
	local btns = {"Apply", "Settings", "Cancel"}
	local main_gui={
		{x=0,y=0,class="label",name="choose_label",label="Please select a script:"},
		{x=1,y=0,class="dropdown",name="tscript",items=dir_table,value=dir_table[1]}
	}
	local btn, res = ADD(main_gui, btns, {ok="Apply", cancel="Cancel"})
    if btn=="Apply" then
		local psya = sc_dir..res["tscript"].."/"..scandir_f(sc_dir..res["tscript"], "yaml") --the path for the yaml file containing controls' spec
		--local psya = "C:/Users/saman/AppData/Roaming/Aegisub/automation/autoload/PythonScripts/SimpleGradient/ParamMaker/y2.yaml"
		local y_in = str_from(psya)
		local controls_table = yaml.eval(y_in)
		local btns2 = controls_table.Buttons
		--local btns2 = {"Apply","Cancel"}
		local inputs_gui={}
		for _, items1 in pairs(controls_table.Controls) do
			table.insert(inputs_gui,{class=items1.class,x=items1.x,y=items1.y,width=items1.width,height=items1.height,label=items1.label,hint=items1.hint,text=items1.text,value=items1.value,min=items1.min,max=items1.max,step=items1.step,items=items1.items})
			--[[if items1.class == "label" then
				table.insert(inputs_gui,{class="label",x=items1.x,y=items1.y,width=items1.width,height=items1.height,label=items1.label})
			elseif items1.class == "edit" then
				table.insert(inputs_gui,{class="edit",x=items1.x,y=items1.y,width=items1.width,height=items1.height,hint=items1.hint,text=items1.text})
			elseif items1.class == "intedit" then
				table.insert(inputs_gui,{class="intedit",x=items1.x,y=items1.y,width=items1.width,height=items1.height,hint=items1.hint,value=items1.value,min=items1.min,max=items1.max})
			elseif items1.class == "floatedit" then
				table.insert(inputs_gui,{class="floatedit",x=items1.x,y=items1.y,width=items1.width,height=items1.height,hint=items1.hint,value=items1.value,min=items1.min,max=items1.max,step=items1.step})
			end]]
		end
		--[[str34 = serializeTable(inputs_gui)
		str35 = serializeTable(btns2)
		l34 = sub[10]
		l34.text = str34
		sub[0] = l34
		l34.text = str35
		sub[0] = l34]]
		local btn2, res2 = ADD(inputs_gui, btns2, {ok=btns[1], cancel=btns[-1]})
		--btn2 = True
		
		if btn2 == btns[1] then
			--Building the string resembling the current subtitle file only with selected line(s) to be sent to the python script.
			local str = ""
			local info_header, style_header = true, true
			for i=1,#sub do
				local l = sub[i]
				if l.class == "info" then
					if info_header then
						if str == "" then
							str = "[Script Info]".."\n".."; Script generated by Python Terminal".."\n".."; http://www.aegisub.org/"
						else
							str = str.."\n\n".."[Script Info]".."\n".."; Script generated by Python Terminal".."\n".."; http://www.aegisub.org/"
						end
						info_header = false
					end
					str = str.."\n"..l.raw
				end
				if l.class == "style" then
					if style_header then
						if str == "" then
							str = "[V4+ Styles]".."\n".."Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
						else
							str = str.."\n\n".."[V4+ Styles]".."\n".."Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
						end
						style_header = false
					end
					str = str.."\n"..l.raw
				end
			end
			str = str.."\n\n".."[Events]".."\n".."Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
			for _, i in ipairs(sel) do
				local l = sub[i]
				str = str.."\n"..l.raw
				l.comment = true
				sub[i] = l
			end
			
			--Saving the created string in a file.
			local out = assert(io.open(sc_dir.."InputSubtitle.ass", "wb"))
			out:write(str)
			assert(out:close())
			
			--Running the python script and getting the result
			local pspa = sc_dir..res["tscript"].."/"..scandir_f(sc_dir..res["tscript"], "py") --the path for the python script
			local handle = io.popen(python_path.." "..pspa.." "..sc_dir)
			--local result = handle:read("*a")
			handle:close()
			--result = result:sub(1,-2)
			
			--Converting the result to ass lines.
			local psya = sc_dir..scandir_f(sc_dir, "txt") --the path for the txt file containing python script output
			local all_lines = lines_from(psya)
			--all_lines = yaml.eval(y_in)
			--[[l7 = sub[10]
			l7.text = s2[3].text
			sub[0] = l7]]
			local l2 = {}
			l2["class"]="dialogue" l2["comment"]=false l2["layer"]=0 l2["start_time"]=0 l2["end_time"]=0 l2["style"]="" l2["actor"]="" l2["margin_l"]=0 l2["margin_r"]=0 l2["margin_t"]=0 l2["effect"]="" l2["text"]=""
			for counter1=1,(#all_lines/11) do
				local line_number = tonumber(all_lines[11*(counter1-1) + 1])
				l2.layer = tonumber(all_lines[11*(counter1-1) + 2])
				l2.start_time = tonumber(all_lines[11*(counter1-1) + 3])
				l2.end_time = tonumber(all_lines[11*(counter1-1) + 4])
				l2.style = all_lines[11*(counter1-1) + 5]
				l2.actor = all_lines[11*(counter1-1) + 6]
				l2.margin_l = tonumber(all_lines[11*(counter1-1) + 7])
				l2.margin_r = tonumber(all_lines[11*(counter1-1) + 8])
				l2.margin_t = tonumber(all_lines[11*(counter1-1) + 9])
				l2.effect = all_lines[11*(counter1-1) + 10]
				l2.text = all_lines[11*(counter1-1) + 11]
				sub.insert(sel[line_number]+1, l2)
			end
			--[[for counter1=1,#all_lines do
				line = all_lines[counter1]
				l2.layer=line.layer l2.start_time=line.start_time l2.end_time=line.end_time l2.style=line.style l2.actor=line.actor l2.margin_l=line.margin_l l2.margin_r=line.margin_r l2.margin_t=line.margin_v l2.effect=line.effect l2.text=line.text
				sub.insert(sel[line.line_number]+1, l2)
			end]]
			--------------------------------------------
		end
	end
	
	aegisub.set_undo_point(script_name)
end

--Source: https://stackoverflow.com/a/11130774
function scandir(directory)
    local i, t, popen = 0, {}, io.popen
	local pfile = popen('dir "'..directory..'" /b /ad')
    for filename in pfile:lines() do
		if filename then
			i = i + 1
			t[i] = filename
		end
    end
    pfile:close()
    return t
end

function scandir_f(directory, ext) --ext: file extension (string)
    local t, popen = "", io.popen
	local pfile = popen('dir "'..directory..'" /b /a-d')
    for filename in pfile:lines() do
		filename = filename:match(".*%."..ext.."$")
		if filename then
			t = filename
		end
    end
    pfile:close()
    return t
end

--Source (with modification): https://stackoverflow.com/a/11204889
-- see if the file exists
function file_exists(file)
  local f = assert(io.open(file, "rb"))
  if f then assert(f:close()) end
  return f ~= nil
end
-- get all lines from a file, returns an empty 
-- list/table if the file does not exist
function lines_from(file)
  if not file_exists(file) then return {} end
  local lines = {}
  for line in io.lines(file) do 
    lines[#lines + 1] = line
  end
  return lines
end
-- get the string from a file, returns nil if the file does not exist
function str_from(file)
  if not file_exists(file) then return nil end
  local f = assert(io.open(file, "rb"))
  local str = f:read("*a")
  assert(f:close())
  return str
end


function serializeTable(val, name, skipnewlines, depth)
    skipnewlines = skipnewlines or false
    depth = depth or 0
    local tmp = string.rep(" ", depth)
    if name then tmp = tmp .. name .. " = " end
    if type(val) == "table" then
        tmp = tmp .. "{" .. (not skipnewlines and "\n" or "")
        for k, v in pairs(val) do
            tmp =  tmp .. serializeTable(v, k, skipnewlines, depth + 1) .. "," .. (not skipnewlines and "\n" or "")
        end
        tmp = tmp .. string.rep(" ", depth) .. "}"
    elseif type(val) == "number" then
        tmp = tmp .. tostring(val)
    elseif type(val) == "string" then
        tmp = tmp .. string.format("%q", val)
    elseif type(val) == "boolean" then
        tmp = tmp .. (val and "true" or "false")
    else
        tmp = tmp .. "\"[inserializeable datatype:" .. type(val) .. "]\""
    end
    return tmp
end


-- Register the macro
aegisub.register_macro(script_name, script_description, main)
