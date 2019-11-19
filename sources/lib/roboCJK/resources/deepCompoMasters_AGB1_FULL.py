"""
Copyright 2019 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
#coding=utf-8
deepCompoMasters = {
"Hanzi" : {'口': [['口', '圞', '扣', '囄', '斖']], '一': [['一']], '木': [['木', '林', '櫜', '梟', '桼', '桽', '㭟'], ['䢶', '闲', '㰐', '鬱']], '艹': [['艹', '虋', '鏾']], '日': [['日', '㬨', '曩', '电']], '氵': [['氵', '㶙', '鼝']], '丶': [['丶']], '月': [['月', '臟', '鸁', '甩'], ['䏍', '鬌', '㔥']], '土': [['土', '壄', '坐', '啬', '䝅', '鷙', '竃', '鱙'], ['㘷', '㚀', '㦳', '鱙']], '亻': [['亻', '虪', '鷹']], '扌': [['扌', '擨', '䳲']], '女': [['女', '䤷', '䆯'], ['如', '㜻', '䭳']], '大': [['大', '鬕','䶝','㻎','㺆','鼷','攆'], ['达','䲅','䲪','牵','臡','㵄','㼽'], ['奏','䡞']], '又': [['又', '嗫', '矍'], ['叒', '难', '鱍']], '十': [['十', '畞', '疐', '協']], '虫': [['虫', '鼜', '䘈', '䗙']], '山': [['山', '㠨', '㟺', '㟗', '両']], '釒': [['釒', '䉧', '钀']], '火': [['火', '礯', '踿', '爨'], ['躞', '灳', '㥕'], ['灲', '爩']], '丿': [['丿']], '人': [['人', '閄', '僰'], ['尒', '㒪'], ['仌', '傘', '从', '内']], '宀': [['宀', '靌', '鼹']], '冖': [['冖', '虋', '㲉']], '王': [['王', '寚', '釜', '朢', '㣆', '蘁', '玉'], ['㺫', '瓛', '靌']], '言': [['言', '謩', '鸑']], '禾': [['禾', '䆐', '䆃', '秦', '秉', '季'], ['囷', '䆐', '黍', '羲']], '田': [['田', '䨻', '鼺']], '心': [['心', '鬡', '鸋']], '⺮': [['⺮', '䉵', '鷑']], '阝': [['阝', '䧰', '騭']], '貝': [['貝', '籯']], '糹': [['糹', '圞']], '目': [['目', '䁿', '矚']], '忄': [['忄', '䱭', '墯']], '八': [['八', '釟'], ['虋'], ['六', '蘷', '黵']], '隹': [['隹', '雦', '䨊']], '夕': [['夕', '濥', '麟', '䵼']], '立': [['立', '麞', '䴙'], ['翊', '䇔']], '辶': [['辶', '韆', '鬔']], '石': [['石', '䃑', '䃧', '䂙', '䂖', '蠹']], '亠': [['亠', '㐯', '飰']], '攵': [['攵', '䶫', '敻']], '广': [['广', '黂', '邝']], '鳥': [['鳥', '鸁', '鶱']], '寸': [['寸', '糰', '寿', '㡡']], '罒': [['罒', '譼']], '魚': [['魚', '鱜', '鯗', '䱘', '鿐']], '力': [['力', '別', '办', '为', '勅', '㔕', '嚽', '䬅']], '夂': [['夂', '㔶'], ['麥', '䵁'], ['処', '櫜', '㰶']], '車': [['車', '䡨', '䡞', '䡾'], ['惠', '蓴', '剸']], '丨': [['丨']], '白': [['白', '鱳', '䀌']], '匕': [['匕', '觺', '雌', '老'], ['比', '爩', '䖇']], '幺': [['幺', '㡫', '䋰', '蠿', '䤕', '㓜']], '巾': [['巾', '讏', '兩', '帇']], '刂': [['刂', '㶜', '鵥']], '足': [['足', '䮿', '躉', '蹇'], ['䟔', '鷺', '躈'], ['䟳']], '𠂉': [['𠂉', '䌫', '䀋']], '丷': [['丷', '㶜', '䆈', '䴆', '宻', '立']], '皿': [['皿', '鬡', '黸'], ['卹', '鸕']], '米': [['米', '麟', '蘪', '糞'], ['夈', '䊱', '㰘']], '厶': [['厶', '黲']], '小': [['小', '靌'], ['尐', '齋', '鿌']], '牛': [['牛', '趱', '牶', '鯯', '午'], ['牝', '犪', '犇']], '尸': [['尸', '戸', '屬', '㶜', '鼊']], '疒': [['疒', '癳', '螏', '蒺']], '刀': [['刀', '䬭', '劎', '䬟']], '工': [['工', '羾', '䨸', '左', '巫'], ['㓚', '彠', '䴒']], '耳': [['耳', '䶫', '饏', '聑', '朂', '聽']], '爫': [['爫', '䨸', '㘥']], '馬': [['馬', '驡', '驘', '驀']], '衤': [['衤', '䙱', '䉱']], '勹': [['勹', '㔪', '齺']], '冂': [['冂', '冎', '丽', '氅'], ['罓', '奥', '虋']], '止': [['止', '䤠', '㒊', '騭'], ['㱐', '㡪']], '戈': [['戈', '盞', '巇', '㦮', '幾', '䶪']], '习': [['习', '躢'], ['䍿', '飂']], '犭': [['犭', '獼', '鸑']], '厂': [['㓹', '欁']], '⻗': [['雪', '䨻']], '彳': [['彳', '豵', '蘌']], '几': [['几', '凡', '贙', '䖕'], ['䢳', '䬌'], ['朵', '船']], '儿': [['儿', '趲', '毤'], ['㒭', '趲']], '門': [['門', '闅', '鷴']], '豆': [['豆', '囍', '靊', '豋'], ['剅', '巇']], '欠': [['欠', '㱍', '蹷']], '灬': [['灬', '灦', '羹', '䍎']], '羊': [['羊', '鲜', '㿏', '䯁', '譱', '羔'], ['羌', '羻', '齹'], ['嚉', '䨴', '轛']], '頁': [['頁', '䫯', '顰']], '𧰨': [['𧰨', '靀', '醵', '豢'], ['逐', '㯻', '䝐'], ['甤', '㶙']], '酉': [['酉', '釅', '虋']], '虍': [['虍', '钀', '齾']], '钅': [['钅', '镟']], '𠘧': [['𠘧', '毈', '毊']], '⺊': [['⺊', '上', '䴞', '䀋']], '穴': [['穴', '鴥', '屄'], ['鴪', '䬒', '䰓']], '㐅': [['㐅', '凶', '㠨']], '𠂇': [['㔫', '鱡', '蠈'], ['右', '龓', '鬌']], '了': [['了', '凾', '驏', '爳']], '斤': [['斤', '鐁', '鍁', '誓']], '万': [['万', '鏇', '鸄']], '䒑': [['䒑', '兰', '䥙', '虁'], ['鐡']], '士': [['士', '䥗', '籉']], '匚': [['匚', '㔶', '䥲', '繄']], '弓': [['弓', '㢴', '獼', '鬻']], '丰': [['丰', '拜', '䎚', '靊', '鬔'], ['寿', '畴', '筹', '綁', '幚']], '干': [['干', '鼡', '平', '衎', '慿', '䶬'], ['䢴', '姸', '屛']], '今': [['今', '令', '癊', '盦'], ['㓧', '衑', '䨄']], '彐': [['彐', '彟', '邍']], '𠂊': [['刍', '䲚', '毚', '亇', '靌']], '彡': [['彡', '丯', '㣊', '㱶', '䰓']], '矢': [['矢', '失', '翭', '簇'], ['劮', '璏', '觺']], '⺌': [['⺌', '龸', '当', '䌃', '㙶']], '革': [['革', '驧', '鞷']], '臼': [['臼', '䑔', '鑿']], '覀': [['覀', '翲', '䴩']], '丂': [['丂', '与', '槬', '灋']], '龶': [['龶', '责', '纛', '䮯']], '示': [['示', '鳚', '䴩']], '耂': [['耂', '老', '孝', '蠩', '鬐']], '飠': [['飠', '飣', '餰', '㔳']], '贝': [['贝', '鹦', '戆']], '纟': [['纟', '橼', '辔']], '犬': [['犬', '钀', '䔸'], ['㹜', '飆', '闃']], '丁': [['丁', '䲗', '鬡']], '㐄': [['㐄', '翷', '䘙']], '礻': [['礻', '鰰', '䴪']], '戊': [['戊', '咸', '鹹', '觱']], '讠': [['讠', '雠', '㺆']], '㔾': [['㔾', '黦', '䵫'], ['剜', '鵷', '䣀']], '廾': [['廾', '丌', '齈', '駴', '鼖']], '中': [['中', '㴢', '㯻']], '勿': [['勿', '鐊', '鸉']], '見': [['見', '欟', '鬹', '覐'], ['覞', '覹', '䨳']], '由': [['由', '甴', '叀', '䵏', '黌']], '比': [['比', '龤', '毚'], ['㩺', '鵾', '㔡']], '兀': [['兀', '䥵', '䲶', '尶', '翹'], ['発', '溌', '㾱'], ['刓', '衏', '㚁']], '舟': [['舟', '䒆', '䰔']], '毛': [['毛', '䶰', '䄟', '毽', '屗'], ['㲎', '膬']], '予': [['予', '櫲', '䰆']], '⺇': [['⺇', '䥚', '飍'], ['䫹', '䬟']], '非': [['非', '釄', '齏'], ['㔐', '䤘']], '业': [['业', '㶙', '鑿'], ['邺', '繊', '戯']], '艮': [['艮', '簋', '檭'], ['退', '螁', '饜']], '𠄌': [['𠄌', '丧', '鱜', '䬟']], '九': [['九', '丸', '雑', '翆', '㐡'], ['汍', '讛', '鷙'], ['頄', '虓']], '冫': [['冫', '冮', '趑', '篛']], '自': [['自', '獿', '䰓']], '𧘇': [['𧘇', '䴋', '鬟'], ['翾', '䴉', '闧']], '走': [['走', '樾', '趣', '㿐']], '水': [['水', '氶', '氷', '㴇', '灥'], ['凼', '㴇', '㵘']], '臣': [['臣', '鑶', '䉯']], '𠃍': [['书', '凸', '裊', '䵻']], '镸': [['镸', '髟', '䦋', '䰓']], '㐱': [['㐱', '㶀', '鬖'], ['剼', '鷚', '㓄']], '可': [['可', '錒', '覉']], '而': [['而', '鴯', '䰑']], '鱼': [['鱼', '鳌', '衡'], ['蓟', '鳚']], '共': [['共', '襶', '㢞'], ['恭', '㿺', '謈']], '氺': [['氺', '函', '顄', '邍'], ['录', '龣', '䴪']], '𡗗': [['𡗗', '春', '㰉', '䆐'], ['㦼', '㔦'], ['菐', '纀', '羮'], ['䴆', '㲫']], '巳': [['巳', '已', '巎', '㡪'], ['剀', '䪱', '㰝', '㱼']], '巴': [['巴', '癰', '裛'], ['䣈']], '瓦': [['瓦', '㽊', '甕', '甅']], '朩': [['朩', '㝳', '余', '鎩', '鎥']], '且': [['且', '鎺', '斖'], ['刞', '鋤', '䴑'], ['縣', '纛']], '𢆉': [['𢆉', '擜', '鑿']], '鹿': [['鹿', '鸝', '麠'], ['䚕', '麣', '麤']], '乚': [['乚', '䎎', '㐂', '㔺'], ['霵', '鬛']], '缶': [['缶', '爩', '䖇', '罋']], '卩': [['卩', '卪', '卫', '報', '䥏', '籞']], '甫': [['甫', '黼', '牖'], ['盙', '鑮', '䰊']], '乙': [['乙', '㨴', '㐣', '氹']], '户': [['户', '顧', '簄']], '廿': [['廿', '丗', '㔮', '臡']], '甲': [['甲', '玂', '厴']], '千': [['千', '瓩', '㪓', '㵇', '䄹'], ['刋', '谸']], '氏': [['氏', '鴟', '䯺']], '回': [['回', '顲', '䯬']], '𠂆': [['𠂆', '乕', '齭', '䖙']], '骨': [['骨', '髍', '䯢']], '角': [['角', '䲒', '觺']], '文': [['文', '䰚', '斖'], ['彣', '珳'], ['这', '癍', '簢']], '开': [['开', '㶜', '䵤']], '㠯': [['㠯', '鶳', '蠥']], '去': [['去', '丢', '灩', '闔']], '黑': [['黑', '虪', '䨹'], ['䵞', '黝', '黴']], '鸟': [['鸟', '䴙', '鹰'], ['鸵', '鹱']], '里': [['里', '甅', '裏'], ['㼿', '嘢', '黙']], '龹': [['龹', '橳', '韏'], ['㓬', '勬']], '车': [['车', '辔', '辇'], ['轧', '辙', '錾']], '至': [['至', '齷', '籉'], ['郅', '㰉', '䦯']], '𠃌': [['𠃌', '刁', '抝', '㴐', '㼩', '书', '裊', '乜'], ['司', '嗣', '䛐']], '爿': [['爿', '䵁', '䵼'], ['鼎', '䵻', '䵼'], ['淵', '蜵', '鼝']], '束': [['束', '觫', '䇿'], ['剌', '䲚', '鷘']], '乛': [['乛', '氶', '买', '敢', '䶫', '夀']], '辰': [['辰', '鋠', '鬞', '蜃'], ['䣅', '䢈', '鷐', '㦺']], '皮': [['皮', '㗞', '蔢'], ['㓟', '㿹', '錃']], '癶': [['癶', '驋', '鼟'], ['㔁', '䠬']], '來': [['來', '㯤', '䵅'], ['郲', '䳵', '麷']], '亡': [['亡', '魍', '籯']], '卜': [['卜', '下', '掛', '麔']], '公': [['公', '㟣', '嵡'], ['颂', '鶲', '蓘']], '弋': [['弋', '虣', '鳶', '貳', '貮']], '鬼': [['鬼', '䰱', '㠢', '䰯']], '生': [['生', '㶙', '䃧'], ['䲼', '剷']], '手': [['手', '掰', '䖂', '㐦']], '其': [['其', '䲉', '㽄'], ['基', '䥓', '藄']], '少': [['少', '緲', '䲵']], '𫝀': [['𫝀', '䪗', '讏']], '门': [['门', '阚', '鹇']], '肀': [['肀', '䏋', '妻', '鷛', '霋']], '句': [['句', '䜘', '驚']], '亨': [['亨', '享', '驐', '鐜']], '不': [['不', '嫑', '噽']], '曲': [['曲', '欁', '鬞', '髷']], '巛': [['巛', '癰', '窼']], '用': [['用', '㶲', '甮', '甩'], ['甬', '鷛', '庸'], ['勇', '䞻']], '果': [['果', '騍', '彚'], ['剿', '臝', '裹'], ['杲', '槕', '桌']], '云': [['云', '靆', '䨺']], '𤴓': [['𤴓', '縦', '翨']], '马': [['马', '骣', '骉']], '世': [['世', '䥡', '屟']], '金': [['金', '鑫', '鑿']], '谷': [['谷', '谿', '㮤'], ['卻', '豅', '螸']], '占': [['占', '檆', '㼭', '㤐']], '内': [['内', '㨥', '㪅'], ['㒷', '竊']], '凵': [['凵', '凾', '詾', '蘻']], '乃': [['乃', '頺', '夃', '㵬', '鼐']], '釆': [['釆', '鐇', '䉒'], ['勫', '飜', '粵', '敹']], '母': [['母', '䲄', '䓯'], ['鳘', '纛']], '尢': [['尢', '蹴', '㮷', '尷']], '出': [['出', '鶌', '㬧']], '也': [['也', '鍦', '䞄', '乸']], '齒': [['齒', '䶫', '齾']], '疋': [['疋', '䰯', '觺']], '壬': [['壬', '鼮', '霪']], '身': [['身', '軅', '麝']], '聿': [['聿', '騝', '書', '䀌']], '直': [['直', '癲', '矗', '悳']], '电': [['电', '龟', '黤', '鼍'], ['剦', '鵪']], '斗': [['斗', '櫆', '㪻']], '匃': [['匃', '蠍', '䨠']], '免': [['免', '䨲', '毚', '嬔']], '𣥂': [['𣥂', '步', '翽', '鬢']], '厃': [['厃', '危', '詹', '甔', '䦲']], '兼': [['兼', '鹻', '鬑'], ['㪠', '鶼', '尲']], '禺': [['禺', '䘈', '躉']], '彑': [['彑', '櫞', '蠡']], '入': [['入', '魎', '鬗']], '页': [['页', '癫', '颦']], '豸': [['豸', '貜', '蠫']], '央': [['央', '醠', '霙', '盎', '鴦'], ['䣐', '䒋', '䦫']], '冏': [['冏', '鷸', '霱']], '衣': [['衣', '銥', '㠢'], ['裁', '䙪']], '必': [['必', '藌', '飋']], '龴': [['龴', '甬', '䰯', '觺']], '旡': [['旡', '兂', '䤐', '蠶'], ['兓', '䤐', '蠶']], '廴': [['廴', '廽', '騝', '閮']], '高': [['高', '髝', '藳']], '卑': [['卑', '䰦', '顰']], '气': [['气', '霼', '氰'], ['㔕', '㡮']], '包': [['包', '颮', '袌']], '瓜': [['瓜', '槬', '攨', '瓝', '㼒'], ['㼌', '㺠', '瓥']], '龰': [['龰', '鏦', '䳷']], '交': [['交', '礮', '筊'], ['䢒', '纐', '㼎']], '俞': [['俞', '瀭', '䵉'], ['㓱', '毹']], '井': [['井', '丼', '琎', '汬'], ['冓', '醸', '嚢']], '龍': [['龍', '龖', '龘']], '鬲': [['鬲', '钀', '齾']], '甘': [['甘', '㵇', '甞', '甝', '䗣']], '柬': [['柬', '钄'], ['㪝', '韊', '籣']], '冉': [['冉', '䶲', '髯']], '𠃊': [['𠃊', '匸', '䜳', '戱'], ['丏', '麪', '髩']], '屮': [['屮', '艸', '㞢', '芔'], ['芻', '雛', '雟', '糱']], '北': [['北', '鉳', '冀', '燕', '醼'], ['邶', '䴏']], '饣': [['饣', '馓']], '我': [['我', '鵝', '鵞']], '婁': [['婁', '䱾', '鷜', '擻', '㟺']], '屰': [['屰', '鳜', '鷢']], '兆': [['兆', '駣', '鼗'], ['頫', '鴵']], '民': [['民', '鴖', '睯']], '乍': [['乍', '齚', '怎']], '卒': [['卒', '醉', '䯿']], '㇏': [['㇏', '刄', '劔', '茰'], ['乁', '亪'], ['派', '虀'], ['覛', '欁'], ['尐']], '⺆': [['⺆', '翢', '䯾']], '𫶧': [['𫶧', '㐬', '宺', '醯', '鎏'], ['㼹']], '牙': [['牙', '鋣', '衺']], '片': [['片', '䥡', '簰'], ['淵', '䨊']], '友': [['友', '鍰', '㬊'], ['鶢']], '僉': [['僉', '鹼', '簽'], ['劍', '瀲', '籢']], '扁': [['扁', '翩', '篇']], '巨': [['巨', '䝣', '螶']], '于': [['于', '䵹']], '乇': [['乇', '馲', '䨋', '亳', '扥', '䣨']], '尗': [['尗', '顣', '蹙'], ['督']], '夭': [['夭', '镺', '䴠'], ['岙', '乔', '㴁'], ['鴁', '鋈']], '光': [['光', '觥', '晃', '兤'], ['尡', '耀']], '亥': [['亥', '豥', '劾', '賌']], '重': [['重', '䵯', '㘒'], ['動', '㷲', '憅']], '弗': [['弗', '梻', '費']], '屯': [['屯', '霕', '萅'], ['邨', '噸']], '尞': [['尞', '飉', '嶚'], ['鹩', '䨅']], '夋': [['夋', '黢', '䈗'], ['逡', '皴']], '𠃜': [['𠃜', '声', '眉', '毊', '篃']], '尹': [['尹', '蛜', '麏', '裠']], '犮': [['犮', '黻', '髮'], ['䳊', '魃']], '六': [['六', '鼆', '㐮']], '介': [['介', '魀', '䯰'], ['界', '鎅']], '丘': [['丘', '駈', '鬓'], ['屔']], '喬': [['喬', '䎗', '毊']], '冘': [['冘', '㴷', '髧', '沊'], ['邥', '䧵']], '\U0002d544': [['\U0002d544', '厳', '敩', '巌']], '曾': [['曾', '囎', '鬙']], '㡀': [['㡀', '䥕', '弊'], ['蟞', '虌']], '鼠': [['鼠', '鼶', '竄']], '咼': [['咼', '鐹', '窩']], '五': [['五', '䢩', '䦜', '㐚']], '面': [['面', '䩋', '靨', '蠠']], '赤': [['赤', '爀', '㬄']], '离': [['离', '䙰', '㒿', '禽']], '甚': [['甚', '磡', '䨢']], '旁': [['旁', '覫', '䨦']], '夬': [['夬', '鴃', '䆕'], ['刔', '䫼', '䦑']], '见': [['见', '觑', '鬶', '觃']], '巠': [['巠', '䪫', '鑋'], ['剄', '巰', '葝']], '乡': [['乡', '鱜', '饔']], '齊': [['齊', '齎', '鱭', '麡']], '申': [['申', '鰰', '䗝']], '爾': [['爾', '獼', '䥸']], '朱': [['朱', '䣷', '鼄'], ['邾', '鴸']], '夌': [['夌', '鯪', '䈊'], ['䬋']], '壽': [['壽', '䬞', '翿', '㦞']], '及': [['及', '觙', '雭']], '叉': [['叉', '㕚', '颾', '鼜']], '冬': [['冬', '鼨', '㲇'], ['䳉', '䶱']], '丽': [['丽', '酾', '逦'], ['婯', '鸝', '籭']], '襄': [['襄', '釀', '鬤'], ['勷', '瓤']], '坴': [['坴', '錴'], ['勎', '㰊', '褻']], '叚': [['叚', '豭', '麚'], ['㰺', '䫗', '蕸']], '侖': [['侖', '溣', '癟']], '𠂭': [['𠂭', '鬯', '鹹', '䖇']], '留': [['留', '飀', '霤']], '𡨄': [['𡨄', '䮿', '騫']], '隶': [['隶', '霴', '䆲'], ['㱂', '靆', '逮']], '更': [['更', '鯾', '莄'], ['䢚', '郠'], ['甦', '㬲']], '弟': [['弟', '䶏', '鬀']], '堇': [['堇', '騹', '䈽'], ['勤', '懄', '懃']], '啇': [['啇', '讁', '藡']], '厷': [['厷', '鈜', '翃', '閎']], '卌': [['卌', '鷡', '橆']], '乂': [['乂', '礟', '図', '笅', '㞿'], ['爻', '礟', '笅']], '會': [['會', '䶐', '鬠'], ['劊', '朇']], '反': [['反', '蝂', '㽹'], ['返', '瓪', '鋬']], '丑': [['丑', '鱃'], ['侴']], '與': [['與', '歟', '㶛', '㠘'], ['㦛', '㐦', '襷']], '祭': [['祭', '鰶', '䕓']], '求': [['求', '鯄', '盚'], ['逑', '䥭', '裘']], '東': [['東', '樄', '螴'], ['㼯', '敶', '䦨']], '半': [['半', '溿', '鵥'], ['判', '叛']], '产': [['产', '産', '㘖', '虄']], '𠂎': [['𠂎', '卵', '㟹', '乮']], '朿': [['朿', '襋', '棗'], ['刺', '襋', '棗']], '孛': [['孛', '餑', '荸'], ['郣', '㴾', '愂']], '倉': [['倉', '鎗', '䤌', '蒼'], ['創', '鶬']], '亦': [['亦', '跡', '弈'], ['恋', '鵉']], '亞': [['亞', '錏', '蝁'], ['㰳', '鵶', '斵']], '長': [['長', '㯑', '鼚']], '垂': [['垂', '䮔', '菙'], ['郵', '䳠']], '黽': [['黽', '鼆', '虌']], '争': [['争', '瀞', '鬇']], '乎': [['乎', '嚹', '乯']], '肅': [['肅', '䎘', '蕭']], '延': [['延', '駳', '䗺']], '帝': [['帝', '鶙', '㛳']], '夷': [['夷', '鴺', '䨑']], '㇉': [['㇉', '丐', '䪢']], '⺄': [['⺄', '䭀', '橩']], '西': [['西', '嗮', '氥']], '㚇': [['㚇', '翪', '鬉']], '𦥯': [['𦥯', '壆', '斆', '䮸']], '龙': [['龙', '拢', '詟', '䶭']], '畏': [['畏', '鰃', '嵔'], ['㞇']], '尺': [['尺', '駅', '昼'], ['咫'], ['迟']], '華': [['華', '鷨', '曅']], '畢': [['畢', '魓', '罼']], '匀': [['匀', '鈞', '鋆']], '典': [['典', '錪', '觍', '䓦'], ['䐌']], '之': [['之', '鴔', '覂']], '㇀': [['㇀', '七', '䟙', '刁']], '巤': [['巤', '鱲', '鬣']], '囱': [['囱', '驄', '窻']], '丩': [['丩', '㔿', '嘂', '䆗']], '㦰': [['㦰', '䤘', '籤']], '龠': [['龠', '䟑', '㿜'], ['龢', '䶵', '籲']], '禹': [['禹', '齲', '䨞']], '韦': [['韦', '韫', '苇']], '疌': [['疌', '疀', '箑']], '爲': [['爲', '鄬', '爳']], '帶': [['帶', '嵽', '䠠']], '川': [['川', '瞓', '氚']], '善': [['善', '鱔']], '丹': [['丹', '雘', '旃']], '𦥑': [['𦥑', '㒨', '虋']], '佥': [['佥', '验', '签'], ['剑', '潋', '蔹']], '久': [['久', '畞', '羐'], ['粂', '柩', '灸'], ['㕗']], '𠃓': [['𠃓', '飏', '烫']], '父': [['父', '䭸', '㸘'], ['㸖', '㵚']], '熏': [['熏', '醺', '薰'], ['勳', '爋', '蘍']], '幾': [['幾', '魕']], '尨': [['尨', '㴳', '㙙']], '尧': [['尧', '骁', '荛', '翘']], '奥': [['奥', '鐭', '嶴'], ['䴈']], '𦣞': [['𦣞', '㺇', '媐']], '臿': [['臿', '敮', '㞚']], '肉': [['肉', '胾', '癵']], '烏': [['烏', '䖚']], '永': [['永', '䘑', '䳮']], '丬': [['丬', '鳉', '酱']], '戉': [['戉', '樾', '䡸']], '卬': [['卬', '䭹', '䀚']], '雋': [['雋', '鐫', '嶲']], '隺': [['隺', '鶴', '靏']], '毌': [['毌', '鏆', '實']], '曳': [['曳', '䎈', '䇩', '曵']], '头': [['头', '黩', '觌', '窦']], '丣': [['丣', '䱖'], ['澑', '飅', '籒']], '齿': [['齿', '龇']], '臾': [['臾', '斔', '䝿'], ['斞']], '才': [['才', '豺', '鼒']], '憂': [['憂', '䥳'], ['鄾', '㱊']], '升': [['升', '髜', '巐']], '乑': [['乑', '驟', '藂'], ['㔌', '鄹']], '爪': [['爪', '爴', '坕'], ['爬', '㸕']], '鬥': [['鬥', '鬬', '鬧']], '以': [['以', '䬮', '苡']], '褱': [['褱', '耲', '蘾']], '来': [['来', '铼', '莱', '赉'], ['慭']], '展': [['展', '囅']], '夜': [['夜', '䤳', '㖱'], ['鵺']], '四': [['四', '駟']], '册': [['册', '銏', '笧']], '东': [['东', '鸫', '岽'], ['胨', '练']], '𠃋': [['𠃋', '乆', '咝', '鸶'], ['㸦', '夨'], ['奊', '捑', '䜁']], '龜': [['龜', '䆋'], ['鬮', '䶰', '龞']], '长': [['长', '涨', '苌']], '肃': [['肃', '鹔', '箫']], '眔': [['眔', '䜚', '㱎']], '爭': [['爭', '靜', '箏']], '州': [['州', '酬', '喌']], '囊': [['囊', '齉']], '具': [['具', '颶', '㮂']], '乐': [['乐', '铄']], '㑒': [['㑒', '鹸'], ['剣', '剱']], '𠃑': [['𠃑', '呉', '㯛', '㡣']], '史': [['史', '駛', '使']], '亙': [['亙', '䱭']], '飛': [['飛', '騛', '飝']], '专': [['专', '啭']], '𡿨': [['𡿨', '婾']], '龵': [['龵', '掰', '看']], '禸': [['禸', '覶', '竊']], '率': [['率', '蟀', '䔞']], '发': [['发', '酦', '废']], '亅': [['亅', '竹', '寜']], '么': [['么', '嬷', '簒']], '為': [['為', '媯', '䈧']], '丱': [['丱', '㺦', '關']], '丈': [['丈', '粀', '㽴']], '㐆': [['㐆', '磤', '慇']], '𣎳': [['朮', '痲', '怷']], '雀': [['雀', '㘍', '蠽']], '粛': [['粛', '繍', '簘']], '年': [['年', '鵇']], '囬': [['囬', '廽', '圗']], '乌': [['乌', '钨'], ['邬']], '丫': [['丫', '虀']], '㇇': [['㇇', '承', '㴍', '詧']], '𤴔': [['𤴔', '疎', '疏', '蔬']], '𠁁': [['㓸', '鬬']], '雨': [['雨', '瘺']], '凹': [['凹', '垇', '兕']], '事': [['事', '䭄']], '⺼': [['⺼', '膧']], '亜': [['亜', '唖', '悪']], '㇣': [['㇣', '㔔', '㫈']], '飞': [['飞']], '赱': [['赱']], '戼': [['戼']], '卐': [['卐']], '卍': [['卍']], '乄': [['乄']], '㇎': [['㇎']], '㇍': [['㇍']], '㇌': [['㇌']], '㇋': [['㇋']]},
}