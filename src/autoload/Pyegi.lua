--[[
You might want to install pyonfx and pyjson through cmd using:
pip install pyonfx
pip install pyjson
]]--

----- Dependencies -----
--include('karaskel.lua')
local json = require 'Azarakhsh.json'

----- Script Info -----
script_name = "Pyegi"
script_description = "Python + Aegisub"
script_version = "0.0.1"
script_author = "DrunkSimurgh & SSgumS"
script_namespace = "Pyegi"

----- Macro Names -----
local main_macro_name = "Pyegi/Pyegi"
local settings_macro_name = "Pyegi/Settings"

----- Variables -----
local ADP
local ADD
local config_dir
local scripts_dir
local settings_filepath
local default_settings = {
	python_path = ""
}

----- Functions -----
local function macro_init() -- aegisub is nil on script's load
	ADP = aegisub.decode_path
	ADD = aegisub.dialog.display
	config_dir = ADP("?user").."/automation/config/Pyegi/"
	scripts_dir = config_dir.."PythonScripts/"
	settings_filepath = config_dir.."settings.json"
end

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
  local f = io.open(file_path, "rb")
  if f then f:close() end
  return f ~= nil
end

-- get all lines from a file, returns an empty 
-- list/table if the file does not exist
local function lines_from(file_path)
  local lines = {}
  for line in io.lines(file_path) do 
    lines[#lines + 1] = line
  end
  return lines
end

-- get the string from a file, returns nil if the file does not exist
local function read_all_file_as_string(file_path)
  local f = assert(io.open(file_path, "rb"))
  local str = f:read("*a")
  assert(f:close())
  return str
end

local function serialize(val, name, skipnewlines, depth)
    skipnewlines = skipnewlines or false
    depth = depth or 0
    local tmp = string.rep(" ", depth)
    if name then tmp = tmp .. name .. " = " end
    if type(val) == "table" then
        tmp = tmp .. "{" .. (not skipnewlines and "\n" or "")
        for k, v in pairs(val) do
            tmp =  tmp .. serialize(v, k, skipnewlines, depth + 1) .. "," .. (not skipnewlines and "\n" or "")
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

local function open_settings()
	-- load current settings
	local settings = default_settings
	if file_exists(settings_filepath) then
		settings = json.decode(read_all_file_as_string(settings_filepath))
		aegisub.log(5, serialize(settings).."\n")
	end

	-- show dialog
	local btns = {"Save", "Cancel"}
	local gui={
		{x=0,y=0,class="label",label="Python Path:"},
		{x=1,y=0,width=25,class="edit",name="python_path",value=settings.python_path}
	}
	local btn, res = ADD(gui, btns, {ok="Save", cancel="Cancel"})

	if btn == btns[1] then
		-- set new values
		for key, value in pairs(res) do
			settings[key] = value
		end

		-- override settings
		local settings_file = assert(io.open(settings_filepath, "wb"))
		settings_file:write(json.encode(settings))
		assert(settings_file:close())
	end
end

function Main(sub, sel)
	macro_init()

	-- select python script
	local dir_table = scandir(scripts_dir)
	local btns = {"Apply", "Settings", "Cancel"}
	local main_gui={
		{x=0,y=0,class="label",label="Please select a script:"},
		{x=1,y=0,class="dropdown",name="tscript",items=dir_table,value=dir_table[1]}
	}
	local btn, res = ADD(main_gui, btns, {ok="Apply", cancel="Cancel"})
	local py_script_name = res.tscript

    if btn == btns[1] then
		-- load python script settings
		local py_settings_filepath = ""
		local py_settings_default_filepath = scripts_dir..py_script_name.."/settings.json"
		local py_settings_override_filepath = scripts_dir..py_script_name.."/settings.override.json"
		if file_exists(py_settings_override_filepath) then
			py_settings_filepath = py_settings_override_filepath
		else
			py_settings_filepath = py_settings_default_filepath
		end
		local py_settings = json.decode(read_all_file_as_string(py_settings_filepath))

		-- add python script's parameters' gui
		local btns2 = py_settings.Buttons
		local inputs_gui={}
		for _, items1 in pairs(py_settings.Controls) do
			table.insert(inputs_gui,{class=items1.class,name=items1.name,x=items1.x,y=items1.y,width=items1.width,height=items1.height,label=items1.label,hint=items1.hint,text=items1.text,value=items1.value,min=items1.min,max=items1.max,step=items1.step,items=items1.items})
		end
		local btn2, res2 = ADD(inputs_gui, btns2, {ok=btns2[1], cancel=btns2[-1]})
		
		if btn2 == btns[1] then
			-- write parameters' value into a file
			local save_table = py_settings
			for _, items1 in pairs(save_table.Controls) do
				items1.value = res2[items1.name]
			end
			local save_str = json.encode(save_table)
			local py_parameters_file_path = os.tmpname()
			aegisub.log(5, serialize(py_parameters_file_path).."\n")
			local py_parameters = assert(io.open(py_parameters_file_path, "wb"))
			py_parameters:write(save_str)
			assert(py_parameters:close())

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

			-- write the created ass script
			local lua_out_file_path = os.tmpname()
			aegisub.log(5, serialize(lua_out_file_path).."\n")
			local lua_out = assert(io.open(lua_out_file_path, "wb"))
			lua_out:write(str)
			assert(lua_out:close())
			
			-- load script settings
			local settings = default_settings
			if file_exists(settings_filepath) then
				settings = json.decode(read_all_file_as_string(settings_filepath))
			end

			-- Running the python script
			local py_out_file_path = os.tmpname()
			aegisub.log(5, serialize(py_out_file_path).."\n")
			local is_py_absolute = settings.python_path ~= ""
			local py_script_path = scripts_dir..res["tscript"].."/main.py"
			local command_parameters_string = ' "'..py_script_path..'" "'..lua_out_file_path..'" "'..py_out_file_path..'" "'..py_parameters_file_path..'"'
			aegisub.log(5, serialize(command_parameters_string).."\n")
			if is_py_absolute then
				assert(os.execute('""'..settings.python_path..'"'..command_parameters_string..'"')) -- TODO: not working on platforms other than windows probably
			else
				assert(os.execute("python"..command_parameters_string))
			end
			
			-- Converting the result to ass lines.
			local all_lines = lines_from(py_out_file_path)
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
	elseif btn == "Settings" then
		open_settings()
	end
	
	aegisub.set_undo_point(main_macro_name)
end

function Settings()
	macro_init()

	open_settings()

	aegisub.set_undo_point(settings_macro_name)
end

-- Register the macro
aegisub.register_macro(main_macro_name, script_description, Main)
-- aegisub.register_macro(settings_macro_name, "Change script's global settings", Settings)
