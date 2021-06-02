--[[
Split into Letters:
Just modified "reanimated" script of NecrosCopy (split letters section) for the persian language.
]]

split_script_name="Parsi/Split Persian Letters"
sokoon_script_name="Parsi/Special Characters/sokoon"
nimfaseleh_script_name="Parsi/Special Characters/nimfaseleh"
peyvastehsaz_script_name="Parsi/Special Characters/peyvastehsaz"
script_description="Some tools for persian language processing."
script_author="ass_karaoke"
script_version="1.1.0"
script_namespace="Parsi"

local utf8 = require 'utf8':init()
re=require'aegisub.re'

include('karaskel.lua')

--	Split into Letters	--	[- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -] [- -]
function space(subs,sel)
	nsel={} for z,i in ipairs(sel) do table.insert(nsel,i) end
	count=0
	for z=#sel,1,-1 do
		i=sel[z]
		line=subs[i]
		text=line.text
		text = utf8.gsub(text, "لا", "ﻻ")
		text = utf8.gsub(text, "هٔ", "ۀ")
		visible=text:gsub("%b{}",""):gsub("%s*\\[Nh]%s*"," ")
		letrz=re.find(visible,".")
		if not text:match "\\p1" and letrz and #letrz>1 then
			sr=stylechk(subs,line.style) -- style reference
			notra=detra(text) -- remove animation tag(s) \t
			acalign=nil
			m1,m2,m3,m4=text:match("\\move%(([%d.-]+),([%d.-]+),([%d.-]+),([%d.-]+)")
			if m1 then
				text=text:gsub("\\move%(([%d.-]+),([%d.-]+)","\\pos(%1,%2)(")
				movX=m3-m1 movY=m4-m2
			end
			text=text:gsub(" *\\[Nh] *"," ")
			if not text:match"\\pos" then text=getpos(subs,text) end
			tags=text:match(STAG) or ""
			after=text:gsub(STAG,""):gsub("{[^\\}]-}","")
			local px,py=text:match("\\pos%(([%d.-]+),([%d.-]+)%)")
			local x1,width,w,wtotal,let,spacing,avgspac,ltrspac,xpos,lastxpos,spaces,prevlet,scx,k1,k2,k3,bord,off,inwidth,wdiff,pp,tpos
			scx=notra:match("^{[^}]-\\fscx([%d%.]+)") or sr.scale_x
			fsp=notra:match("^{[^}]-\\fsp([%d%.]+)")
			if fsp then sr.spacing=tonumber(fsp) end
			fsize=notra:match("^{[^}]-\\fs([%d%.]+)")
			if fsize then sr.fontsize=tonumber(fsize) end
			phont=notra:match("^{[^}]-\\fn([^\\}]+)")
			if phont then sr.fontname=phont end
			bord=notra:match("^{[^}]-\\bord([%d%.]+)") or sr.outline
			k1,k2,k3=text:match("clip%(([%d.-]+),([%d.-]+),([%d.-]+),")
			letters={}	wtotal=0
			
			for l=1,#letrz do
				local post1 = ""
				ltr=split_per(letrz,l)
				if utf8.len(ltr) > 1 then
					ltr_temp = utf8.sub(ltr,1,1)
					post1 = utf8.gsub(ltr,ltr_temp,"")
					ltr = ltr_temp
				end
				w=aegisub.text_extents(sr,ltr)
				table.insert(letters,{l=ltr..post1,w=w})
				wtotal=wtotal+w
				leng=re.find(ltr,'.')
				if ltr=="" then
					logg("- Line #"..i-line0..": re module failure: letter lost - #"..l)
				elseif #leng>1 then
					logg("- Line #"..i-line0..": re module failure: multiple letters matched: "..ltr)
				end
			end
			if #letters~=#letrz then
				logg(#letrz.." -> "..#letrz)
			end
			intags={}	cnt=0
			for chars,tag in after:gmatch("([^}]+)({\\[^}]+})") do
				pp=re.find(chars,".")
				tpos=#pp+1+cnt
				intags[tpos]=tag
				cnt=cnt+#pp
			end
			spacing=res.space
			avgspac=wtotal/#letters
			off=(letters[1].w-letters[#letters].w)/4*scx/100
			inwidth=(wtotal-letters[1].w/2-letters[#letters].w/2)*scx/100
			if spacing==1 then spacing=round(avgspac*scx)/100 end
			width=(#letters-1)*spacing	--off
			
			-- klip-based stuff
			if k1 then 
				width=(k3-k1)-letters[1].w/2*(scx/100)-letters[#letters].w/2*(scx/100)-(2*bord)
				spacing=(width+2*bord)/(#letters-1)
				px=(k1+k3)/2-off
				tags=tags:gsub("\\i?clip%b()","")
			end
			
			-- find starting x point based on alignment
			if not acalign then acalign=text:match("\\an(%d)") or sr.align end
			acalign=tostring(acalign)
			if acalign:match("[147]") then
				tags=tags:gsub("\\an%d",""):gsub("^{","{\\an"..acalign+1)
				:gsub("\\pos%(([%d.-]+)",function(p) return "\\pos("..round(p+(wtotal/2)*(scx/100),2) end)
			end
			if acalign:match("[369]") then
				tags=tags:gsub("\\an%d",""):gsub("^{","{\\an"..acalign-1)
				:gsub("\\pos%(([%d.-]+)",function(p) return "\\pos("..round(p-(wtotal/2)*(scx/100),2) end)
			end
			if not k1 then px,py=tags:match("\\pos%(([%d.-]+),([%d.-]+)%)") end
			acalign=tags:match("\\an(%d)")
			x1=round(px+width/2)
			
			wdiff=(width-inwidth)/(#letters-1)
			lastxpos=x1
			spaces=0
			-- weird letter-width sorcery starts here
			for t=1,#letters do
				let=letters[t]
				if t>1 then
					prevlet=letters[t-1]
					ltrspac=(let.w+prevlet.w)/2*scx/100+wdiff
					ltrspac=round(ltrspac,2)
				else
					fact1=spacing/(avgspac*scx/100)
					fact2=(let.w-letters[#letters].w)/4*scx/100
					ltrspac=round(fact1*fact2,2)
				end
				if intags[t] then tags=tags..intags[t] tags=tagmerge(tags) tags=duplikill(tags) end
				t2=tags..utf8.gsub(let.l, "ﻻ", "لا")
				xpos=lastxpos-ltrspac
				XP=xpos
				notra=detra(t2)
				rota=notra:match("^{[^}]-\\frz([-%d.]+)")
				if rota then
					h=px-xpos
					X=math.cos(math.rad(rota))*h
					Y=math.sin(math.rad(rota))*h
					x=round(px-X,1)
					y=round(py+Y,1)
					t2=t2:gsub("\\pos%b()","\\pos("..x..","..y..")")
				else
					t2=t2:gsub("\\pos%(([%d.-]+),([%d.-]+)%)","\\pos("..XP..",%2)")
				end
				if m1 then
					t2=t2:gsub("\\pos%(([%d.-]+),([%d.-]+)%)%(,[%d.-]+,[%d.-]+",function(a,b) return "\\move("..a..","..b..","..a+movX..","..b+movY end)
				end
				lastxpos=xpos
				l2=line
				l2.text=t2
				if t==1 then text=t2 else no_line1 = " ‌ًَُِِّْٔ" inl_temp = utf8.gsub(let.l,"([%(%)%[%]%.])","a7") inl1 = utf8.find(no_line1, inl_temp)
				if inl1 == nil then subs.insert(i+t-1-spaces,l2) nsel=shiftsel(nsel,i,1) else count=count-1 spaces=spaces+1 end
				end
			end
			count=count+#letters-1
			line.text=text
			subs[i]=line
		end
	end
	return nsel
end

function split_per(letrz,l)
	local ltr=letrz[l].str
	local post1=""
	local grp1 = "آادذرزژوؤأۀﻻ"
	local grp2 = "بپتثجچحخسشصضطظعغفقکگلمنهیئـي"
	local grp1_s1 = "ﺂﺎﺪﺬﺮﺰﮋﻮﺆﺄﮥﻼ"
	local grp2_s1 = "ﺒﭙﺘﺜﺠﭽﺤﺨﺴﺸﺼﻀﻄﻈﻌﻐﻔﻘﮑﮕﻠﻤﻨﻬﯿﺌـﻴ"
	local grp2_s2 = "ﺐﭗﺖﺚﺞﭻﺢﺦﺲﺶﺺﺾﻂﻆﻊﻎﻒﻖﮏﮓﻞﻢﻦﻪﯽﺊـﻲ" -- pre-connection
	local grp2_s3 = "ﺑﭘﺗﺛﺟﭼﺣﺧﺳﺷﺻﺿﻃﻇﻋﻏﻓﻗﮐﮔﻟﻣﻧﻫﯾﺋـﻳ" -- post-connection
	local grp3 = "ًَُِّْٔ" -- harakat
	local pos1 = false -- false: no pre-connection, true: pre-connection
	local pos2 = false -- false: no post-connection, true: post-connection
	ltr_temp = utf8.gsub(ltr,"([%)%(%]%[%.])","")
	if ltr_temp ~= "" and ltr ~= "ء" then
		ist1 = utf8.find(grp1, ltr)
		ist2 = utf8.find(grp2, ltr)
		if ist1 ~= nil or ist2 ~= nil then
			if l ~= 1 then
				local ltr2=letrz[l-1].str
				ltr_temp2 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
				if ltr_temp2 ~= "" then
					i0 = utf8.find(grp3, ltr2)
					counter1 = 1
					while i0 ~= nil do
						counter1 = counter1 + 1
						ltr2=letrz[l-counter1].str
						ltr_temp3 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
						if ltr_temp3 ~= "" then
							i0 = utf8.find(grp3, ltr2)
						else
							i0 = nil
						end
					end
					ltr_temp4 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
					if ltr_temp4 ~= "" then
						i1 = utf8.find(grp2, ltr2)
						if i1 ~= nil then pos1 = true end
					end
				end
			end
			if l ~= #letrz then
				local ltr2=letrz[l+1].str
				ltr_temp2 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
				if ltr_temp2 ~= "" then
					i0 = utf8.find(grp3, ltr2)
					counter1 = 1
					while i0 ~= nil and l+counter1 ~= #letrz do
						counter1 = counter1 + 1
						post1 = post1..ltr2
						ltr2=letrz[l+counter1].str
						ltr_temp3 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
						if ltr_temp3 ~= "" then
							i0 = utf8.find(grp3, ltr2)
						else
							i0 = nil
						end
					end
					ltr_temp4 = utf8.gsub(ltr2,"([%(%)%[%]%.])","")
					if ltr_temp4 ~= "" then
						i1 = utf8.find(grp1, ltr2)
						i2 = utf8.find(grp2, ltr2)
						if i1 ~= nil or i2 ~= nil then pos2 = true end
					end
				end
			end
			i1 = utf8.find(grp1, ltr)
			i2 = utf8.find(grp2, ltr)
			if i1 ~= nil then
				if pos1 then ltr = utf8.sub(grp1_s1,i1,i1) end
			end
			if i2 ~= nil then
				if pos1 and pos2 then ltr = utf8.sub(grp2_s1,i2,i2) end
				if pos1 and not pos2 then ltr = utf8.sub(grp2_s2,i2,i2) end
				if not pos1 and pos2 then ltr = utf8.sub(grp2_s3,i2,i2) end
			end
		end
		ist3 = utf8.find(grp3, ltr)
		if ist3 ~= nil and ltr ~= " " then ltr = "‌" end
	end
	ltr = utf8.gsub(ltr,"%(","a1") ltr = utf8.gsub(ltr,"%)","a2") ltr = utf8.gsub(ltr,"a1",")") ltr = utf8.gsub(ltr,"a2","(")
	ltr = utf8.gsub(ltr,"%[","a1") ltr = utf8.gsub(ltr,"%]","a2") ltr = utf8.gsub(ltr,"a1","]") ltr = utf8.gsub(ltr,"a2","[")
	ltr = utf8.gsub(ltr,"»","a1") ltr = utf8.gsub(ltr,"«","a2") ltr = utf8.gsub(ltr,"a1","«") ltr = utf8.gsub(ltr,"a2","»")
	ltr = ltr..post1
	return ltr
end

--	reanimatools	------------------------------------------------------------------------------------------------------------------------------------
function round(n,dec) dec=dec or 0 n=math.floor(n*10^dec+0.5)/10^dec return n end
function detra(t) return t:gsub("\\t%b()","") end
function tagmerge(t) repeat t,r=t:gsub("({\\[^}]-)}{(\\[^}]-})","%1%2") until r==0 return t end
function t_error(message,cancel) aegisub.dialog.display({{class="label",label=message}},{"OK"},{close='OK'}) if cancel then aegisub.cancel() end end
function shiftsel(sel,i,mode)
	if i<sel[#sel] then
	for s=1,#sel do if sel[s]>i then sel[s]=sel[s]+1 end end
	end
	if mode==1 then table.insert(sel,i+1) end
	table.sort(sel)
	return sel
end

function stylechk(subs,sn)
  for i=1,#subs do
    if subs[i].class=="style" then
      local st=subs[i]
      if sn==st.name then sr=st break end
    end
  end
  if sr==nil then t_error("Style '"..sn.."' doesn't exist.",1) end
  return sr
end

function getpos(subs,text)
    st=nil defst=nil
    for g=1,#subs do
        if subs[g].class=="info" then
			local k=subs[g].key
			local v=subs[g].value
			if k=="PlayResX" then resx=v end
			if k=="PlayResY" then resy=v end
        end
		if resx==nil then resx=0 end
		if resy==nil then resy=0 end
        if subs[g].class=="style" then
            local s=subs[g]
			if s.name==line.style then st=s break end
			if s.name=="Default" then defst=s end
        end
		if subs[g].class=="dialogue" then
			if defst then st=defst else t_error("Style '"..line.style.."' not found.\nStyle 'Default' not found. ",1) end
			break
		end
    end
    if st then
		acleft=st.margin_l	if line.margin_l>0 then acleft=line.margin_l end
		acright=st.margin_r	if line.margin_r>0 then acright=line.margin_r end
		acvert=st.margin_t	if line.margin_t>0 then acvert=line.margin_t end
		acalign=st.align	if text:match("\\an%d") then acalign=text:match("\\an(%d)") end
		aligntop="789" alignbot="123" aligncent="456"
		alignleft="147" alignright="369" alignmid="258"
		if alignleft:match(acalign) then horz=acleft
		elseif alignright:match(acalign) then horz=resx-acright
		elseif alignmid:match(acalign) then horz=resx/2 end
		if aligntop:match(acalign) then vert=acvert
		elseif alignbot:match(acalign) then vert=resy-acvert
		elseif aligncent:match(acalign) then vert=resy/2 end
		end
		if horz>0 and vert>0 then 
		if not text:match("^{\\") then text="{\\rel}"..text end
		text=text:gsub("^({\\[^}]-)}","%1\\pos("..horz..","..vert..")}") :gsub("\\rel","")
    end
    return text
end

function duplikill(tagz)
	local tags1={"blur","be","bord","shad","xbord","xshad","ybord","yshad","fs","fsp","fscx","fscy","frz","frx","fry","fax","fay"}
	local tags2={"c","2c","3c","4c","1a","2a","3a","4a","alpha"}
	tagz=tagz:gsub("\\t%b()",function(t) return t:gsub("\\","|") end)
	for i=1,#tags1 do
	    tag=tags1[i]
	    repeat tagz,c=tagz:gsub("|"..tag.."[%d%.%-]+([^}]-)(\\"..tag.."[%d%.%-]+)","%1%2") until c==0
	    repeat tagz,c=tagz:gsub("\\"..tag.."[%d%.%-]+([^}]-)(\\"..tag.."[%d%.%-]+)","%2%1") until c==0
	end
	tagz=tagz:gsub("\\1c&","\\c&")
	for i=1,#tags2 do
	    tag=tags2[i]
	    repeat tagz,c=tagz:gsub("|"..tag.."&H%x+&([^}]-)(\\"..tag.."&H%x+&)","%1%2") until c==0
	    repeat tagz,c=tagz:gsub("\\"..tag.."&H%x+&([^}]-)(\\"..tag.."&H%x+&)","%2%1") until c==0
	end
	repeat tagz,c=tagz:gsub("\\fn[^\\}]+([^}]-)(\\fn[^\\}]+)","%2%1") until c==0
	repeat tagz,c=tagz:gsub("(\\[ibusq])%d(.-)(%1%d)","%2%3") until c==0
	repeat tagz,c=tagz:gsub("(\\an)%d(.-)(%1%d)","%3%2") until c==0
	tagz=tagz:gsub("(|i?clip%(%A-%))(.-)(\\i?clip%(%A-%))","%2%3")
	:gsub("(\\i?clip%b())(.-)(\\i?clip%b())",function(a,b,c)
	    if a:match("m") and c:match("m") or not a:match("m") and not c:match("m") then return b..c else return a..b..c end end)
	tagz=tagz:gsub("|","\\"):gsub("\\t%([^\\%)]-%)","")
	return tagz
end

function split_persian_letters(subs,sel)
	ATAG="{[*>]?\\[^}]-}"
	STAG="^{>?\\[^}]-}"
	res=res or {space=1,ccol=true,cpstyle=true,c1=true,grad=true}
	sel=space(subs,sel)
	return sel
end

function sokoon(subs,sel)
	for _, i1 in ipairs(sel) do
		local l1 = subs[i1]
		text1 = l1.text
		l1.text = text1.."ْ"
		subs[i1] = l1
	end
	aegisub.set_undo_point(sokoon_script_name)
end

function nimfaseleh(subs,sel)
	for _, i1 in ipairs(sel) do
		local l1 = subs[i1]
		text1 = l1.text
		l1.text = text1.."‌"
		subs[i1] = l1
	end
	aegisub.set_undo_point(nimfaseleh_script_name)
end

function peyvastehsaz(subs,sel)
	for _, i1 in ipairs(sel) do
		local l1 = subs[i1]
		text1 = l1.text
		l1.text = text1.."‍"
		subs[i1] = l1
	end
	aegisub.set_undo_point(peyvastehsaz_script_name)
end

aegisub.register_macro(split_script_name,script_description,split_persian_letters)
aegisub.register_macro(sokoon_script_name,script_description,sokoon)
aegisub.register_macro(nimfaseleh_script_name,script_description,nimfaseleh)
aegisub.register_macro(peyvastehsaz_script_name,script_description,peyvastehsaz)