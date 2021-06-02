--[[
You might want to install pyonfx and pyjson through cmd using:
pip install pyonfx
pip install pyjson
]]--

script_name = "Pyegi"
script_description = "."
script_version = "0.0.1"
script_author = "DrunkSimurgh & SSgumS"
script_namespace = "Pyegi"

--include('karaskel.lua')
local json = require 'Azarakhsh.json'

-- Source: https://stackoverflow.com/a/11130774
local function scandir(directory)
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

local function scandir_f(directory, ext) --ext: file extension (string)
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

-- Source (with modification): https://stackoverflow.com/a/11204889
-- see if the file exists
local function file_exists(file_path)
  local f = assert(io.open(file_path, "rb"))
  if f then assert(f:close()) end
  return f ~= nil
end

-- get all lines from a file, returns an empty 
-- list/table if the file does not exist
local function lines_from(file_path)
  if not file_exists(file_path) then return {} end
  local lines = {}
  for line in io.lines(file_path) do 
    lines[#lines + 1] = line
  end
  return lines
end

-- get the string from a file, returns nil if the file does not exist
local function str_from(file_path)
  if not file_exists(file_path) then return nil end
  local f = assert(io.open(file_path, "rb"))
  local str = f:read("*a")
  assert(f:close())
  return str
end

local function serializeTable(val, name, skipnewlines, depth)
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

function Main(sub, sel)
	local ADP = aegisub.decode_path
	local ADD = aegisub.dialog.display

	local config_dir = ADP("?user").."/automation/config/Pyegi/"
	local scripts_dir = config_dir.."PythonScripts/" -- the path to the python scripts
	local dir_table = scandir(scripts_dir)
	
	local btns = {"Apply", "Settings", "Cancel"}
	local main_gui={
		{x=0,y=0,class="label",name="choose_label",label="Please select a script:"},
		{x=1,y=0,class="dropdown",name="tscript",items=dir_table,value=dir_table[1]}
	}
	local btn, res = ADD(main_gui, btns, {ok="Apply", cancel="Cancel"})
	local python_script_name = res["tscript"]
    if btn=="Apply" then
		local settings_filepath = ""
		local settings_default_filepath = scripts_dir..python_script_name.."/settings.json"
		local settings_override_filepath = scripts_dir..python_script_name.."/settings.override.json"
		if file_exists(settings_override_filepath) then
			settings_filepath = settings_override_filepath
		else
			settings_filepath = settings_default_filepath
		end
		local settings = json.decode(str_from(settings_filepath))
		local btns2 = settings.Buttons
		local inputs_gui={}
		for _, items1 in pairs(settings.Controls) do
			table.insert(inputs_gui,{class=items1.class,name=items1.name,x=items1.x,y=items1.y,width=items1.width,height=items1.height,label=items1.label,hint=items1.hint,text=items1.text,value=items1.value,min=items1.min,max=items1.max,step=items1.step,items=items1.items})
		end
		local btn2, res2 = ADD(inputs_gui, btns2, {ok=btns2[1], cancel=btns2[-1]})
		
		if btn2 == btns[1] then
			-- Write parameters' file
			local save_table = settings
			for _, items1 in pairs(save_table.Controls) do
				items1.value = res2[items1.name]
			end
			local save_str = json.encode(save_table)
			local python_parameters_file_path = os.tmpname()
			aegisub.log(5, serializeTable(python_parameters_file_path).."\n")
			local python_parameters = assert(io.open(python_parameters_file_path, "wb"))
			python_parameters:write(save_str)
			assert(python_parameters:close())

			-- Building the string resembling the current subtitle file only with selected line(s) to be sent to the python script.
			local str = ""
			local info_header, style_header = true, true
			for i=1,#sub do
				local l = sub[i]
				if l.class == "info" then
					if info_header then
						if str == "" then
							str = "[Script Info]".."\n".."; Script generated by Pyegi".."\n".."; http://www.aegisub.org/"
						else
							str = str.."\n\n".."[Script Info]".."\n".."; Script generated by Pyegi".."\n".."; http://www.aegisub.org/"
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
				-- Comment lines
				l.comment = true
				sub[i] = l
			end

			-- Write the created ass script
			local lua_out_file_path = os.tmpname()
			aegisub.log(5, serializeTable(lua_out_file_path).."\n")
			local lua_out = assert(io.open(lua_out_file_path, "wb"))
			lua_out:write(str)
			assert(lua_out:close())
			
			-- Running the python script
			local python_out_file_path = os.tmpname()
			aegisub.log(5, serializeTable(python_out_file_path).."\n")
			local python_script_path = scripts_dir..res["tscript"].."/main.py"
			local command = 'python "'..python_script_path..'" "'..lua_out_file_path..'" "'..python_out_file_path..'" "'..python_parameters_file_path..'"'
			aegisub.log(5, serializeTable(command).."\n")
			local result, _, exit = os.execute(command)
			if not result then
				error("Python script exited with status code "..serializeTable(exit)..".")
			end
			
			-- Converting the result to ass lines.
			local all_lines = lines_from(python_out_file_path)
			local l2 = {}
			local line_params_number = 11
			l2["class"]="dialogue" l2["comment"]=false l2["layer"]=0 l2["start_time"]=0 l2["end_time"]=0 l2["style"]="" l2["actor"]="" l2["margin_l"]=0 l2["margin_r"]=0 l2["margin_t"]=0 l2["effect"]="" l2["text"]=""
			for counter1=1,(#all_lines/line_params_number) do
				local line_number = tonumber(all_lines[line_params_number*(counter1-1) + 1])
				l2.layer = tonumber(all_lines[line_params_number*(counter1-1) + 2])
				l2.start_time = tonumber(all_lines[line_params_number*(counter1-1) + 3])
				l2.end_time = tonumber(all_lines[line_params_number*(counter1-1) + 4])
				l2.style = all_lines[line_params_number*(counter1-1) + 5]
				l2.actor = all_lines[line_params_number*(counter1-1) + 6]
				l2.margin_l = tonumber(all_lines[line_params_number*(counter1-1) + 7])
				l2.margin_r = tonumber(all_lines[line_params_number*(counter1-1) + 8])
				l2.margin_t = tonumber(all_lines[line_params_number*(counter1-1) + 9])
				l2.effect = all_lines[line_params_number*(counter1-1) + 10]
				l2.text = all_lines[line_params_number*(counter1-1) + 11]
				sub.insert(sel[line_number]+1, l2)
			end
		end
	end
	
	aegisub.set_undo_point(script_name)
end

-- Register the macro
aegisub.register_macro(script_name, script_description, Main)
