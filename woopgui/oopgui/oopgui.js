function Oopgui(){
    var self = this;
    self.keckID = '';
    self.userdefs = {};
    self.baseurl = 'http://localhost:50100';
    self.offdefs = {
        Stare:[[0,0]],
        Box4:[[0,0], [1,0], [1,-1], [0,-1]],
        Box5:[[0,0],[-1,1],[1,1],[1,-1],[-1,-1]],
        Box9:[[0,0],[-1,1],[-1,-1],[1,1],[1,-1],[-1,0],[1,0],[0,1],[0,-1]]
    };
    self.filters = ['Opn','Y','J','Hbb','Kp','Zbb','Jn1','Jn2','Jn3',
        'Hn1','Hn2','Hn3','Hn4','Hn5','Kn1','Kn2','Kn3','Kn4','Kn5',
        'Zn3','Brγ','Kcnt','HeIB','Paγ','FeII','Hcnt','Drk'];
    self.masks = ['Open Circ','Pupil View','Large Ann','Small Ann','Large Hex','Small Hex'];
    self.maskAnno = {'Open Circ':'O','Pupil View':'P','Large Ann':'A','Small Ann':'a','Large Hex':'H','Small Hex':'h'};
    self.filterSets = [];
    self.timeLeft = 0;

    function El(id) { return document.getElementById(id); };

    function formatGET(vars) {
        var qry = "";
        for (val in vars){
            qry += val + "=" + vars[val] + "&";
        }
        qry = qry.slice(0,qry.length-1);
        return qry;
    };

    self.getFile = function() {
        fileDialogue = El('file-input');
        fileDialogue.click();
    };

    self.openDDF = function() {
        //var file = e.target.files[0];
        var fileDialogue = El('file-input');
        var file = fileDialogue.files[0];
        if(!file) {
            console.log("could not load file");
            return;
        }
        var reader = new FileReader();
        reader.readAsText(file);
        //reader.onerror = errorHandler;
        //reader.onprogress = updateProgress;
        reader.onabort = function(e) {
            alert('File read cancelled');
        };
        reader.onload = function(e){
            self.clearFields();
            var output = e.target.result;
            output = output.split('\n');

            var userdefs = [];

            for (var i=0; i<output.length; i++) {
                var line = output[i];

                if (/<ddf/.exec(line)) {
                    var value = /type=".+"/.exec(line)[0];
                    value = value.substring(6,value.length-1);
                    El('targType').value = value;
                }
                else if (/<dataset/.exec(line)) {
                    var value = /name=".+?"/.exec(line)[0];
                    value = value.substring(6,value.length-1);
                    El('dataset').value = value;

                    //value = /setnum=".+?"/.exec(line);
                    //value = value[0].substring(10,value[0].length-1);
                    //El('setnum').value = value;

                    value = /aomode=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    if (/NGS/.exec(value)) El('aoType').value = value;
                    else {
                        var lgs = value.split('_');
                        El('aoType').value = lgs[0];
                        El('lgsMode').value = lgs[1];
                    }
                    self.enableLGS();

                    //value = /status=".+?"/.exec(line);
                    //value = value[0].substring(10,value[0].length-1);
                    //El('status').value = value;
                }
                else if (/<object>/.exec(line)) {
                    var value = />.+</.exec(line)[0];
                    value = value.substring(1,value.length-1);
                    El('object').value = value;
                }
                else if (/<spec/.exec(line)) {
                    var value = /filter=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    El('specFilter').value = value;

                    value = /scale=".+?&/.exec(line)[0];
                    value = value.substring(7, value.length-1);
                    El('scale').value = value;

                    value = /itime=".+?"/.exec(line)[0];
                    value = value.substring(7,value.length-1);
                    El('specItime').value = parseFloat(value);

                    value = /coadds=".+?"/.exec(line)[0];
                    value = value.substring(8, value.length-1);
                    El('specCoadds').value = parseFloat(value);
                }
                else if (/<imag /.exec(line)) {
                    var value = /mode=".+?"/.exec(line)[0];
                    value = value.substring(6,value.length-1);
                    if (value === "Disabled (Spec only)") value = "Disabled";
                    else if (value === "Independent (Imager only)") value = "Independent";
                    else if (value === "Slave 1: Maximum Repeats") value = "Slave1";
                    else if (value === "Slave 2: Maximum Itime") value = "Slave2";
                    else if (value === "Slave 4: Filter Sets") value = "Slave4";
                    El('imgMode').value = value;

                    self.setMode();
                }
                else if (/<imagFrame/.exec(line)) {
                    var imgMode = El('imgMode').value;
                    var temp = '';

                    var value = /filter=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    if (imgMode == 'Slave4') {
                        temp = El('imgFilterSets');
                        if (temp.value.length == 0) temp.value = value;
                        else temp.value = temp.value + ',' + value;
                    }
                    else El('imgFilter').value = value;

                    value = /mask=".+?"/.exec(line)[0];
                    if (value.length > 0) value = value.substring(6,value.length-1);
                    else value = 'Open Circ';
                    if (imgMode == 'Slave4'){
                        temp.value = temp.value + '-' + self.maskAnno[value];
                    }
                    else El('mask').value = value;

                    value = /itime=".+?"/.exec(line)[0];
                    value = value.substring(7,value.length-1);
                    temp = El('itimeSets');
                    if (imgMode == 'Slave4') {
                        if (temp.value.length == 0) temp.value = value;
                        else temp.value = temp.value + ',' + value;
                    }
                    else El('imgItime').value = parseFloat(value);

                    value = /coadds=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    temp = El('coaddSets');
                    if (imgMode == 'Slave4'){
                        if (temp.value.length == 0) temp.value = value;
                        else temp.value = temp.value + ',' + value;
                    }
                    else El('imgCoadds').value = parseFloat(value);

                    value = /repeats=".+?"/.exec(line)[0];
                    value = value.substring(9, value.length-1);
                    temp = El('repeatSets');
                    if (imgMode == 'Slave4') {
                        if (temp.value.length == 0) temp.value = value;
                        else temp.value = temp.value + ',' + value;
                    }
                    else El('repeats').value = parseFloat(value);
                }
                else if (/<objectDither/.exec(line)) {
                    var value = /type=".+?"/.exec(line)[0];
                    value = value.substring(6, value.length-1);
                    El('objPattern').value = value;

                    value = /frames1=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('objFrames1').value = value;

                    value = /frames2=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('objFrames2').value = value;

                    value = /xOffset=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('initOffX').value = parseFloat(value);

                    value = /yOffset=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('initOffY').value = parseFloat(value);

                    value = /param1=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    El('objLenX').value = parseFloat(value);

                    value = /param2=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    El('objHgtY').value = parseFloat(value);

                    self.objMode();
                }
                else if (/<skyDither/.exec(line)) {
                    var value = /type=".+?"/.exec(line)[0];
                    value = value.substring(6, value.length-1);
                    El('skyPattern').value = value;

                    value = /frames1=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('skyFrames1').value = parseFloat(value);

                    value = /frames2=".+?"/.exec(line)[0];
                    value = value.substring(9,value.length-1);
                    El('skyFrames2').value = parseFloat(value);

                    value = /nodXOffset=".+?"/.exec(line)[0];
                    value = value.substring(12,value.length-1);
                    El('nodOffX').value = parseFloat(value);

                    value = /nodYOffset=".+?"/.exec(line)[0];
                    value = value.substring(12,value.length-1);
                    El('nodOffY').value = parseFloat(value);

                    value = /param1=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    El('skyLenX').value = parseFloat(value);

                    value = /param2=".+?"/.exec(line)[0];
                    value = value.substring(8,value.length-1);
                    El('skyHgtY').value = parseFloat(value);

                    self.skyMode();
                }
                else if (/<ditherPattern/.exec(line)) {
                    var value = /coords=".+?"/.exec(line)[0];
                    value = value.substring(8, value.length-1);
                    El('coordSys').value = value;

                    value = /units=".+?"/.exec(line)[0];
                    value = value.substring(7, value.length-1);
                    El('units').value = value;

                    value = /skyPA=".+?"/.exec(line)[0];
                    value = value.substring(7, value.length-1);
                    El('pa').value = parseFloat(value);
                }
                else if (/<ditherPos/.exec(line)) {
                    var value = /xOff=".+?"/.exec(line)[0];
                    value = value.substring(6,value.length-1);
                    userdefs.push(parseFloat(value));

                    value = /yOff=".+?"/.exec(line)[0];
                    value = value.substring(6,value.length-1);
                    userdefs.push(parseFloat(value));

                    value = /sky=".+?"/.exec(line)[0];
                    value = value.substring(5,value.length-1);
                    if (value === "true") userdefs.push(true);
                    else userdefs.push(false);
                }
            }
            console.log(userdefs);
            //El('userdefs').value = userdefs;
            self.defs = userdefs;
            self.update();
        };
    };

    self.setDDF = function() {
        var fname = prompt('Please enter the file name: ', 'default.ddf');
        if (fname) {
            if (fname.indexOf(".ddf") === -1) fname += ".ddf";
            El('ddfname').value = fname;
        }
        return fname;
    };

    self.saveDDF = function() {
        fname = El('ddfname');
        fname.value = self.setDDF();
        var params = self.createQstr('save_to_file');
        var fileurl = formatGET(params);
        var link = document.createElement('a');
        //link.href = 'oopgui.php?'+fileurl;
        link.href = self.baseurl+'/save_to_file?'+fileurl;
        link.download = fname.value;
        console.log('value of fname:\t', fname.value);
        link.target = "_blank";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        //ajaxPost(self.baseurl+'/save_to_file', params, callback);
    };

    self.saveDB = function() {
        function callback(data) {
            console.log('Result from save:', data);
        }

        fname = El('ddfname');
        fname.value = self.setDDF();
        var params = self.createQstr("save_to_db");
        ajaxPost(self.baseurl+'/save_to_db', params, callback);
    };

    self.loadDB = function() {
        function callback(result) {
            console.log('Loaded from DB');
            console.log(result);
            self.dbResult = result;
            form = El('dbList');
            while(form.hasChildNodes()) {
                form.removeChild(form.lastChild);
            }
            for (i=0; i<result.length; i++) {
                input = document.createElement('input');
                input.type = 'radio';
                input.name = 'ddffile';
                input.value = i;
                input.innerHTML = result[i]['ddfname'];
                form.appendChild(input);
                form.appendChild(document.createTextNode(result[i]['ddfname']));
                form.appendChild(document.createElement('br'));
            }
        }
        El('dbCell').style = 'display: block';
        El('dbPreview').style = 'display: block';

        var params = self.createQstr("load_from_db");
        //console.log('load params: ', params);
        ajaxPost(self.baseurl+'/load_from_db', params, callback);
    };

    self.loadPreview = function() {
        var radios = document.getElementsByName('ddffile');
        var index = -1;
        for (var i=0, len = radios.length; i<len; i++){
            if (radios[i].checked) {
                index = radios[i].value;
                break;
            }
        }
        var display = El('dbDisplay');
        var content = "";
        self.configToLoad = self.dbResult[index];
        while(display.hasChildNodes()){
            display.removeChild(display.lastChild);
        }
        for (var key in self.configToLoad) {
            content = key + ": " + self.configToLoad[key];
            display.appendChild(document.createTextNode(content));
            display.appendChild(document.createElement('br'));
        }
        El('loadConfig').style = "display:block";
    }

    self.loadConfig = function() {
        El('ddfname').value = self.configToLoad.ddfname;
        El('imgMode').value = self.configToLoad.imgMode;
        El('dataset').value = self.configToLoad.dataset;
        El('object').value = self.configToLoad.object;
        El('targType').value = self.configToLoad.targType;
        El('coordSys').value = self.configToLoad.coordSys;
        El('aoType').value = self.configToLoad.aoType;
        El('lgsMode').value = self.configToLoad.lgsMode
        El('units').value = self.configToLoad.units;
        El('pa').value = self.configToLoad.pa;
        El('specFilter').value = self.configToLoad.specFilter;
        El('scale').value = self.configToLoad.scale;
        El('specCoadds').value = parseFloat(self.configToLoad.specCoadds);
        El('specItime').value = parseFloat(self.configToLoad.specItime);
        El('initOffX').value = parseFloat(self.configToLoad.initOffX);
        El('initOffY').value = parseFloat(self.configToLoad.initOffY);
        El('objPattern').value = self.configToLoad.objPattern;
        El('objFrames1').value = parseFloat(self.configToLoad.objFrames1);
        El('objFrames2').value = parseFloat(self.configToLoad.objFrames2);
        El('objLenX').value = parseFloat(self.configToLoad.objLenX);
        El('objHgtY').value = parseFloat(self.configToLoad.objHgtY);
        El('imgFilter').value = self.configToLoad.imgFilter;
        El('mask').value = self.configToLoad.mask;
        El('repeats').value = parseFloat(self.configToLoad.repeats);
        El('imgCoadds').value = parseFloat(self.configToLoad.imgCoadds);
        El('imgItime').value = parseFloat(self.configToLoad.imgItime);
        El('nodOffX').value = parseFloat(self.configToLoad.nodOffX);
        El('nodOffY').value = parseFloat(self.configToLoad.nodOffY);
        El('skyPattern').value = self.configToLoad.skyPattern;
        El('skyFrames1').value = parseFloat(self.configToLoad.skyFrames1);
        El('skyFrames2').value = parseFloat(self.configToLoad.skyFrames2);
        El('skyLenX').value = parseFloat(self.configToLoad.skyLenX);
        El('skyHgtY').value = parseFloat(self.configToLoad.skyHgtY);
        self.defs = self.configToLoad.defs;

        El('dbCell').style = 'display: none';
        El('dbPreview').style = 'display: none';
        El('loadConfig').style = 'display: none';
        self.update();
    };

    self.setCookie = function(key, val, exdays) {
        var d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        var expires = 'expires=' + d.toGMTString();
        document.cookie = key + '+' + val + ';' + expires + ';path=/';
    };

    self.checkCookie = function() {
       // var keckid = self.getKeckID();
       var keckid = 4224;
       // if (keckid != '' && keckid != undefined) return keckid;
       // else { 
       //     window.location.href = "../../login.php?referrer=ObservingTools/oopgui/oopgui.html";
       // }
        return keckid;
    };

    self.getKeckID = function() {
        var allcookies = document.cookie;
        console.log(allcookies);
        var cookies = allcookies.split(';');
        for (var i=0; i < cookies.length; i++) {
            name = cookies[i].split('=')[0];
            value = cookies[i].split('=')[1];
            if (name == 'keckID') return value;
        }
        return '';
    };

    self.showFile = function() {
        El("loadfile").classList.toggle("show");
    };

    window.onclick = function(event) {
        if (!event.target.matches('.dropbtn')) {
            var dropdowns = document.getElementsByClassName('dropdown-content');
            var i;
            for (i=0; i<dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show')
                }
            }
        }
    };

    self.enableLGS = function () {
        var aomode = El('aoType');
        if (aomode.value == 'LGS') {
            El('lgsMode').disabled = false;
        }
        else {
            El('lgsMode').disabled = true;
        }
    };

    self.checkFilter = function() {
        var filter = El('specFilter').value;
        var scale = El('scale');
        switch (filter) {
            case 'Kcb':
            case 'Kc3':
            case 'Kc4':
            case 'Kc5':
                scale.value = '0.10';
                scale.disabled = true;
                break;
            default:
                scale.disabled = false;
                break;
        }
    };

    self.objMode = function () {
        var pattern = El('objPattern');
        if (pattern.value == "None") {
            self.userdefs = {};
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            El('objFrames1').disabled = true;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            El('objOffLenStepX').innerHTML = "None: ";
            El('objOffHgtStepY').innerHTML = "None: ";
        }
        else if (pattern.value == "Stare") {
            self.userdefs = {};
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            var objFrames = El('objFrames1');
            objFrames.disabled = true;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            objFrames.value = 1;
            El('objOffLenStepX').innerHTML = "Unused: ";
            El('objOffHgtStepY').innerHTML = "Unused: ";
        }
        else if (pattern.value== "Statistical Dither") {
            self.userdefs = {};
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            El('objFrames1').disabled = false;
            El('objLenX').disabled = false;
            El('objHgtY').disabled = false;
            El('objOffLenStepX').innerHTML = 'Region Length: ';
            El('objOffHgtStepY').innerHTML = 'Region Height: ';
        }
        else if (pattern.value == "Raster Scan") {
            self.userdefs = {};
            El('objFrames1').disabled = false;
            El('objLenX').disabled = false;
            El('objHgtY').disabled = false;
            El('objOffLenStepX').innerHTML = 'X Stepsize: ';
            El('objOffHgtStepY').innerHTML = 'Y Stepsize: ';
            El('objRaster').style.display = 'block';
            El('objFramesCell').setAttribute("colspan", 2);
        }
        else if (pattern.value == "User Defined") {
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            El('objFrames1').disabled = false;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            El('objOffLenStepX').innerHTML = 'Unused: ';
            El('objOffHgtStepY').innerHTML = 'Unused: ';
        }
        else {
            self.userdefs = {};
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            var frames = El('objFrames1');
            frames.disabled = true;
            El('objLenX').disabled = false;
            El('objHgtY').disabled = false;
            El('objOffLenStepX').innerHTML = 'X Offset: ';
            El('objOffHgtStepY').innerHTML = 'Y Offset: ';
            if (pattern.value == 'Box4') {
                frames.value = 4;
            }
            else if (pattern.value == 'Box5') {
                frames.value = 5;
            }
            else {
                frames.value = 9;
            }
        }
    };

    self.skyMode = function () {
        var pattern = El('skyPattern');
        if (pattern.value == "None") {
            self.userdefs = {};
            El('nodOffX').disabled = true;
            El('nodOffY').disabled = true;
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
            El('skyFrames1').disabled = true;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            El('skyOffLenStepX').innerHTML = "None: ";
            El('skyOffHgtStepY').innerHTML = "None: ";
        }
        else if (pattern.value == "Stare") {
            self.userdefs = {};
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
            var skyFrames = El('skyFrames1');
            skyFrames.disabled = true;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            skyFrames.value = 1;
            El('skyOffLenStepX').innerHTML = "Unused: ";
            El('skyOffHgtStepY').innerHTML = "Unused: ";
        }
        else if (pattern.value== "Statistical Dither") {
            self.userdefs = {};
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyFrames1').disabled = false;
            El('skyLenX').disabled = false;
            El('skyHgtY').disabled = false;
            El('skyOffLenStepX').innerHTML = 'Region Length: ';
            El('skyOffHgtStepY').innerHTML = 'Region Height: ';
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
        }
        else if (pattern.value == "Raster Scan") {
            self.userdefs = {};
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyFrames1').disabled = false;
            El('skyLenX').disabled = false;
            El('skyHgtY').disabled = false;
            El('skyOffLenStepX').innerHTML = 'X Stepsize: ';
            El('skyOffHgtStepY').innerHTML = 'Y Stepsize: ';
            El('skyRaster').style.display = 'block';
            El('skyFramesCell').setAttribute("colspan", 2);
        }
        else if (pattern.value == "User Defined") {
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyFrames1').disabled = false;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            El('skyOffLenStepX').innerHTML = 'Unused: ';
            El('skyOffHgtStepY').innerHTML = 'Unused: ';
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
        }
        else {
            self.userdefs = {};
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            var frames = El('skyFrames1');
            frames.disabled = true;
            El('skyLenX').disabled = false;
            El('skyHgtY').disabled = false;
            El('skyOffLenStepX').innerHTML = 'X Offset: ';
            El('skyOffHgtStepY').innerHTML = 'Y Offset: ';
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
            if (pattern.value == 'Box4') {
                frames.value = 4;
            }
            else if (pattern.value == 'Box5') {
                frames.value = 5;
            }
            else {
                frames.value = 9;
            }
        }
    };

    self.setMode = function () {
        var mode = El('imgMode');
        if (mode.value == 'Disabled') {
            El('specFilter').disabled = false;
            El('scale').disabled = false;
            El('specCoadds').disabled = false;
            El('specItime').disabled = false;
            El('imgFilter').disabled = true;
            El('mask').disabled = true;
            El('repeats').disabled = true;
            El('imgCoadds').disabled = true;
            El('imgItime').disabled = true;
            El('oneFilter').hidden = false;
            El('multiFilter').hidden = true;
            El('oneRepeat').hidden = false;
            El('multiRepeat').hidden = true;
            El('oneCoadds').hidden = false;
            El('multiCoadds').hidden = true;
            El('oneItime').hidden = false;
            El('multiItime').hidden = true;
            El('showFilterSets').hidden = true;
            El('spec').style.backgroundColor = 'lightblue';
            El('imag').style.backgroundColor = '#ffa';
            El('both').style.backgroundColor = '#ffa';
        }
        else if (mode.value == 'Independent') {
            El('specFilter').disabled = true;
            El('scale').disabled = true;
            El('specCoadds').disabled = true;
            El('specItime').disabled = true;
            El('imgFilter').disabled = false;
            El('mask').disabled = false;
            El('repeats').disabled = false;
            El('imgCoadds').disabled = false;
            El('imgItime').disabled = false;
            El('oneFilter').hidden = false;
            El('multiFilter').hidden = true;
            El('oneRepeat').hidden = false;
            El('multiRepeat').hidden = true;
            El('oneCoadds').hidden = false;
            El('multiCoadds').hidden = true;
            El('oneItime').hidden = false;
            El('multiItime').hidden = true;
            El('showFilterSets').hidden = true;
            El('spec').style.backgroundColor = '#ffa';
            El('imag').style.backgroundColor = 'lightblue';
            El('both').style.backgroundColor = '#ffa';
        }
        else if (mode.value == 'Slave4') {
            El('specFilter').disabled = false;
            El('scale').disabled = false;
            El('specCoadds').disabled = false;
            El('specItime').disabled = false;
            El('oneFilter').hidden = true;
            El('multiFilter').hidden = false;
            El('oneRepeat').hidden = true;
            El('multiRepeat').hidden = false;
            El('oneCoadds').hidden = true;
            El('multiCoadds').hidden = false;
            El('oneItime').hidden = true;
            El('multiItime').hidden = false;
            El('showFilterSets').hidden = false;
            El('spec').style.backgroundColor = '#ffa';
            El('imag').style.backgroundColor = '#ffa';
            El('both').style.backgroundColor = 'lightblue';
        }
        else {
            El('specFilter').disabled = false;
            El('scale').disabled = false;
            El('specCoadds').disabled = false;
            El('specItime').disabled = false;
            El('imgFilter').disabled = false;
            El('mask').disabled = false;
            El('repeats').disabled = false;
            El('imgCoadds').disabled = false;
            El('imgItime').disabled = false;
            El('oneFilter').hidden = false;
            El('multiFilter').hidden = true;
            El('oneRepeat').hidden = false;
            El('multiRepeat').hidden = true;
            El('oneCoadds').hidden = false;
            El('multiCoadds').hidden = true;
            El('oneItime').hidden = false;
            El('multiItime').hidden = true;
            El('showFilterSets').hidden = true;
            El('spec').style.backgroundColor = '#ffa';
            El('imag').style.backgroundColor = '#ffa';
            El('both').style.backgroundColor = 'lightblue';
            if (mode.value == 'Slave1') {
                El('repeats').disabled = true;
            }
            else if (mode.value == 'Slave2') {
                El('imgItime').disabled = true;
            }
        }
    };

    self.setMask = function(src, mode) {
        var filter = src;
        var mask = null;
        if (mode == 'multi') mask = src.parentNode.parentNode.cells[1].firstChild;
        else mask = El('mask');

        // All the image filters with no Pupil View and a Large Annular default
        var no_pupil_A = {
            'Y': true,
            'J': true,
            'Hbb': true,
            'Zbb': true,
            'Zn3': true,
            'HeIB': true
        };

        // All the image filters with no Pupil View and a Small Annular default
        var no_pupil_a = {
            'Kp' : true,
            'Kn1': true,
            'Kn2': true,
            'Kn3': true,
            'Kn4': true,
            'Kn5': true,
            'Brγ': true,
            'Kcnt': true
        };

        // All the image filters with a Pupil View and a Large Annular default
        var pupil = {
            'Jn1': true,
            'Jn2': true,
            'Jn3': true,
            'Hn1': true,
            'Hn2': true,
            'Hn3': true,
            'Hn4': true,
            'Paγ': true,
            'FeII': true,
            'Hcnt': true
        };

        // Change the available masks based on image filter
        // Mask = ['Open Circ', 'Pupil View', 'Large Ann', 'Small Ann', 'Large Hex', 'Small Hex']
        if(filter.value == 'Opn') {
            mask[0].hidden = false;
            mask[0].selected  = true;
            mask[1].hidden = false;
            mask[1].selected  = false;
            mask[2].hidden = false;
            mask[2].selected  = false;
            mask[3].hidden = false;
            mask[3].selected  = false;
            mask[4].hidden = false;
            mask[4].selected  = false;
            mask[5].hidden = false;
            mask[5].selected  = false;
        }
        else if (filter.value in no_pupil_A) {
            mask[0].hidden = false;
            mask[0].selected  = false;
            mask[1].hidden = true;
            mask[1].selected  = false;
            mask[2].hidden = false;
            mask[2].selected  = true;
            mask[3].hidden = false;
            mask[3].selected  = false;
            mask[4].hidden = false;
            mask[4].selected  = false;
            mask[5].hidden = false;
            mask[5].selected  = false;
        }
        else if (filter.value in no_pupil_a) {
            mask[0].hidden = false;
            mask[0].selected  = false;
            mask[1].hidden = true;
            mask[1].selected  = false;
            mask[2].hidden = false;
            mask[2].selected  = false;
            mask[3].hidden = false;
            mask[3].selected  = true;
            mask[4].hidden = false;
            mask[4].selected  = false;
            mask[5].hidden = false;
            mask[5].selected  = false;
        }
        else if (filter.value in pupil) {
            mask[0].hidden = true;
            mask[0].selected  = false;
            mask[1].hidden = false;
            mask[1].selected  = false;
            mask[2].hidden = false;
            mask[2].selected  = true;
            mask[3].hidden = true;
            mask[3].selected  = false;
            mask[4].hidden = true;
            mask[4].selected  = false;
            mask[5].hidden = true;
            mask[5].selected  = false;
        }
        else if (filter.value == 'Hn5') {
            mask[0].hidden = true;
            mask[0].selected  = false;
            mask[1].hidden = true;
            mask[1].selected  = false;
            mask[2].hidden = false;
            mask[2].selected  = true;
            mask[3].hidden = false;
            mask[3].selected  = false;
            mask[4].hidden = false;
            mask[4].selected  = false;
            mask[5].hidden = false;
            mask[5].selected  = false;
        }
        else if (filter.value == 'Drk') {
            mask[0].hidden = false;
            mask[0].selected  = true;
            mask[1].hidden = true;
            mask[1].selected  = false;
            mask[2].hidden = true;
            mask[2].selected  = false;
            mask[3].hidden = true;
            mask[3].selected  = false;
            mask[4].hidden = true;
            mask[4].selected  = false;
            mask[5].hidden = true;
            mask[5].selected  = false;
        }
    };

    self.clickFilterSets = function() {
        self.showFilterSets(true);
    };

    self.showFilterSets = function(isBeingShown) {
        var filterSets = El('filterSets');
        var setDefs = El('setDefs');
        El('timeLeft').value = self.calculateImagerTime() - self.calculateUsedTime();

        //var count = self.createFilterSets();
        self.updateFilterSets();
        if (isBeingShown && filterSets.style.display != 'block') filterSets.style.display = 'block';
        else filterSets.style.display = 'none';
    };

    self.updateFilterSets = function() {
        var filterSets = El('setDefs');
        var numFilterSets = filterSets.rows.length;
        var count = 0;

        var filters = El('imgFilterSets');
        filters.value = '';
        var repeats = El('repeatSets');
        repeats.value = '';
        var coadds = El('coaddSets');
        coadds.value = '';
        var imgItime = El('itimeSets');
        imgItime.value = '';

        for (var row of filterSets.rows){
            if (count != 0){
                filters.value = filters.value+','+row.cells[0].firstChild.value+'-'+self.maskAnno[row.cells[1].firstChild.value];
                repeats.value = repeats.value+','+row.cells[2].firstChild.value;
                coadds.value = coadds.value+','+row.cells[3].firstChild.value;
                imgItime.value = imgItime.value+','+row.cells[4].firstChild.value;
            }
            count++;
        }
        filters.value = filters.value.substring(1);
        repeats.value = repeats.value.substring(1);
        coadds.value = coadds.value.substring(1);
        imgItime.value = imgItime.value.substring(1);
    };

    self.calculateImagerTime = function() {
        /*
        Function to calculate the total time for imager exposure
        Uses the coadds and itime from the spec to create a
        maximum upper bound.
        It is used by the Slave4 - Filter Sets mode to limit
        the exposures.

        Returns the calculated maximum upper bound as a float.
        */
        var coadds = El('specCoadds').value;
        var itime = El('specItime').value;
        const BASE_ITIME = 1.476;
        const BASE_OVERHEAD = 0.048;
        var coeff_itime = Math.floor(itime / 1.476);

        // This is some sort of exposure padding
        // It maxes out at +6 for itime multiples of 1.476 greater than 3
        switch (coeff_itime) {
            case 1:
                coeff_itime += 3;
                break;
            case 2:
                coeff_itime += 4;
                break;
            case 3:
                coeff_itime += 5;
                break;
            default:
                coeff_itime += 6;
                break;
        }

        // In order to calculate the total exposure time for the imager
        // we need to calculate the closest multiplier without going over.
        // Then we add the base overhead of 0.048 to it and multiply for
        // each coadd exposure.
        var total_time = ((coeff_itime * BASE_ITIME) + BASE_OVERHEAD) * coadds;
        return total_time;
    };

    self.calculateUsedTime = function(){
        /*
        Reverse engineered from the oopgui upgrade on VM-OSIRISSERVER
        Each exposure has an additional 3.0 seconds associated with it.
        Each repeat above the initial adds an extra 7 seconds on top of that.
        */
        var filterTable = El('setDefs');
        const BASE_OVERHEAD = 3.0;
        const EXTRA_OVERHEAD = 7.0;
        var usedTime = 0;
        var index = 0;
        for (var row of filterTable.rows){
            // Check to see if this is the header row. If it is, skip it.
            if ( index == 0 ) {
                index++;
                continue;
            }
            console.log('0: ', usedTime);
            var repeats = parseInt(row.cells[2].firstChild.value);
            var coadds = parseInt(row.cells[3].firstChild.value);
            var itime = parseInt(row.cells[4].firstChild.value);
            console.log('repeats: ', repeats, '\ncoadds: ', coadds, '\nitime: ', itime);
            usedTime = usedTime + repeats*coadds*(BASE_OVERHEAD+itime) + (repeats-1)*EXTRA_OVERHEAD;
            console.log('1: ', usedTime);
            index++;
        }
        console.log('2: ', usedTime, '\n');
        return usedTime;
    };

    self.checkRepeatTime = function() {
        var timeLeft = self.calculateImagerTime() - self.calculateUsedTime();
        El('timeLeft').value = timeLeft;
        if (timeLeft <= 0) {
            alert('WARNING: Repeats is too large!\nFilter set must fit within one spectrometer frame.');
        }
    };

    self.checkCoaddTime = function() {
        var timeLeft = self.calculateImagerTime() - self.calculateUsedTime();
        El('timeLeft').value = timeLeft;
        if ( timeLeft <= 0) {
            alert('WARNING: Coadds is too large!\nFilter set must fit within one spectrometer frame.');
        }
    };

    self.checkItimeTime = function() {
        var timeLeft = self.calculateImagerTime() - self.calculateUsedTime();
        El('timeLeft').value = timeLeft;
        if ( timeLeft <= 0) {
            alert('WARNING: Itime is too large!\nFilter set must fit within one spectrometer frame.');
        }
    };

    self.addRow = function(rowCount) {
        const MIN_TIME = 5.0;
        var filterTable = El('setDefs');
        var newRow = document.createElement('tr');

        // Check to see if we have enough time to add a new frame
        var totalImagerTime = self.calculateImagerTime();
        var usedTime = self.calculateUsedTime();
        var newTime = totalImagerTime - usedTime - MIN_TIME;
        if (newTime < 0){
            alert("WARNING: A new imager frame cannot be added because there is not enough time within the spectrometer frame.");
            return;
        }
        El('timeLeft').value = newTime;

        // Add the filter options to the row
        var newCell = newRow.insertCell(0);
        var newElement = self.createDropdown(self.filters);
        newElement.onchange = function(){setMask(this, 'multi')};
        newCell.appendChild(newElement);

        // Add the mask options to the row
        newCell = newRow.insertCell(1);
        newElement = self.createDropdown(self.masks);
        newCell.appendChild(newElement);

        // Add a text input for Repeats, default 1
        newCell = newRow.insertCell(2);
        newElement = document.createElement('input');
        newElement.value = 1;
        newElement.onchange = function(){checkRepeatTime()};
        newCell.appendChild(newElement);

        // Add a text input for Coadds, default 1
        newCell = newRow.insertCell(3);
        newElement = document.createElement('input');
        newElement.value = 1;
        newElement.onchange = function(){checkCoaddTime()};
        newCell.appendChild(newElement);

        // Add a text input for Itime, default 2.0
        newCell = newRow.insertCell(4);
        newElement = document.createElement('input');
        newElement.value = 2.0;
        newElement.onchange = function(){checkItimeTime()};
        newCell.appendChild(newElement);

        // Add a button to remove the row
        newCell = newRow.insertCell(5);
        newElement = document.createElement('button');
        newElement.innerHTML = 'Remove Row';
        newElement.onclick = function(src){removeRow(this)};
        newCell.appendChild(newElement);

        // Add the new row to the table
        filterTable.appendChild(newRow);
    };

    self.removeRow = function(src) {
        var table = El('setDefs');
        table.deleteRow(src.parentNode.parentNode.rowIndex);

        // Recalculate the timeLeft
        var timeLeft = self.calculateImagerTime() - self.calculateUsedTime();
        El('timeLeft').value = timeLeft;
    };

    self.clearAllRows = function() {
        var table = El('setDefs');
        for (var i = table.rows.length - 1; i > 0; i--) {
            table.deleteRow(i);
        }
        El('timeLeft').value = self.calculateImagerTime();
    };

    self.createDropdown = function(elements) {
        var newSelect = document.createElement('select');
        for (var option of elements){
            var newOption = document.createElement('option');
            newOption.value = option;
            newOption.innerHTML = option;
            newSelect.appendChild(newOption);
        }
        return newSelect;
    };

    self.clickPosBtn = function() {
        self.showPosList(true);
    };

    self.updateFiltersets = function () {};

    self.showPosList = function (isBeingShown) {
        var userdefs = El('userdefs');

        var count = self.createObjList();
        self.createSkyList(count);
        if (isBeingShown && userdefs.style.display != 'block') userdefs.style.display = 'block';
        else userdefs.style.display = 'none';
    };

    self.createObjList = function() {
        var numObjFrames;
        var objPattern = El('objPattern').value;
        if (objPattern=='None') numObjFrames = 0;
        else numObjFrames = El('objFrames1').value;
        var count = 0;
        var initOffX = parseFloat(El('initOffX').value);
        var initOffY = parseFloat(El('initOffY').value);
        var objLenX = parseFloat(El('objLenX').value);
        var objHgtY = parseFloat(El('objHgtY').value);

        // Remove any previous object nodes
        var table = El('objDefs');
        while(table.hasChildNodes()) {
            table.removeChild(table.lastChild);
        }

        // Append new child nodes
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = '#';
        cell = row.insertCell(1);
        cell.innerHTML = 'Xoff (")';
        cell = row.insertCell(2);
        cell.innerHTML = 'Yoff (")'; 
        cell = row.insertCell(3);
        cell.innerHTML = 'Sky?';

        // Loop through the number of frames and add a row for each one
        for(i=0; i<numObjFrames; i++) {
            row = document.createElement('tr');
            cell = document.createElement('td');
            cell.innerHTML = count;
            row.appendChild(cell);
            cell = document.createElement('td');
            var value = 0;
            if(objPattern!='User Defined') {
                value = self.offdefs[objPattern][i][0]+initOffX+objLenX;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            if(objPattern!='User Defined') {
                value = self.offdefs[objPattern][i][1]+initOffY+objHgtY;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = "<input type='checkbox' unchecked disabled>";
            row.appendChild(cell);
            table.appendChild(row);
            count += 1;
        }
        return count;
    };

    self.createSkyList = function(count) {
        var numSkyFrames;
        var skyPattern = El('skyPattern').value;
        if (skyPattern=='None') numSkyFrames = 0;
        else numSkyFrames = El('skyFrames1').value;
        var initOffX = parseFloat(El('initOffX').value);
        var initOffY = parseFloat(El('initOffY').value);
        var nodOffX = parseFloat(El('nodOffX').value);
        var nodOffY = parseFloat(El('nodOffY').value);
        var skyLenX = parseFloat(El('skyLenX').value);
        var skyHgtY = parseFloat(El('skyHgtY').value);

        // Remove any previous sky nodes
        var table = El('skyDefs');
        while(table.hasChildNodes()) {
            table.removeChild(table.lastChild);
        }

        // Append new child nodes
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        for(i=0; i<numSkyFrames; i++) {
            row = document.createElement('tr');
            cell = document.createElement('td');
            cell.innerHTML = count;
            row.appendChild(cell);
            cell = document.createElement('td');
            var value = 0;
            if(skyPattern != 'User Defined') {
                value = self.offdefs[skyPattern][i][0]+initOffX+nodOffX+skyLenX;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            if(skyPattern!='User Defined') {
                value = self.offdefs[skyPattern][i][1]+initOffY+nodOffY+skyHgtY;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = "<input type='checkbox' checked disabled>";
            row.appendChild(cell);
            table.appendChild(row);
            count += 1;
        }
    };

    self.storeDefs = function() {
        var objTable = El('objDefs');
        var skyTable = El('skyDefs');
        var objPattern = El('objPattern').value;
        var skyPattern = El('skyPattern').value;
        var numrows = parseFloat(El('objFrames1').value)
            + parseFloat(El('skyFrames1').value) + 1;
        var t = [];

        for(var i=1; row=objTable.rows[i]; i++){
            var r = [];
            r.push(row.cells[1].lastChild.value);
            r.push(row.cells[2].lastChild.value);
            if(row.cells[3].lastChild.checked==true)
                r.push(true);
            else r.push(false);
            t.push(r);
        }
        for(var i=1; row=skyTable.rows[i]; i++){
            var r = [];
            r.push(row.cells[1].lastChild.value);
            r.push(row.cells[2].lastChild.value);
            if(row.cells[3].lastChild.checked==true)
                r.push(true);
            else r.push(false);
            t.push(r);
        }

        self.defs = t;
        console.log(self.defs);
        El('userdefs').style.display = 'None';
        self.update();
    };

    self.createQstr = function(serverFunc) {
        // Check for disabled boxes
        var objFrames = El('objFrames1');
        var objLenX = El('objLenX');
        var objHgtY = El('objHgtY');
        var nodOffX = El('nodOffX');
        var nodOffY = El('nodOffY');
        var skyFrames = El('skyFrames1');
        var skyLenX = El('skyLenX');
        var skyHgtY = El('skyHgtY');

        if (objLenX.disabled == true) objLenX = 1.0;
        else objLenX = objLenX.value;
        if (objHgtY.disabled == true) objHgtY = 1.0;
        else objHgtY = objHgtY.value;
        if (nodOffX.disabled == true) nodOffX = 0.0;
        else nodOffX = nodOffX.value;
        if (nodOffY.disabled == true) nodOffY = 0.0;
        else nodOffY = nodOffY.value;
        if (skyLenX.disabled == true) skyLenX = 1.0;
        else skyLenX = skyLenX.value;
        if (skyHgtY.disabled == true) skyHgtY = 1.0;
        else skyHgtY = skyHgtY.value;

        //if (typeof(self.defs) != typeof({})) self.defs = null;

        var params = {
            //'Cmd': serverFunc,
            'keckID':self.checkCookie(),
            'semid':El('pcodelist').value,
            'ddfname':El('ddfname').value,
            'imgMode':El('imgMode').value,
            'dataset':escape(El('dataset').value),
            'object':escape(El('object').value),
            'targType':El('targType').value,
            'coordSys':El('coordSys').value,
            'aoType':El('aoType').value,
            'lgsMode':El('lgsMode').value,
            'units':El('units').value,
            'pa':El('pa').value,
            'specFilter':El('specFilter').value,
            'scale':El('scale').value,
            'specCoadds':El('specCoadds').value,
            'specItime':El('specItime').value,
            'initOffX':El('initOffX').value,
            'initOffY':El('initOffY').value,
            'objPattern':El('objPattern').value,
            'objFrames1':El('objFrames1').value,
            'objFrames2':El('objFrames2').value,
            'objLenX':objLenX,
            'objHgtY':objHgtY,
            'imgFilter':(imgMode == 'Slave4' ? El('imgFilterSets').value : El('imgFilter').value),
            'mask':El('mask').value,
            'repeats':(imgMode == 'Slave4' ? El('repeatSets').value : El('repeats').value),
            'imgCoadds':(imgMode == 'Slave4' ? El('coaddSets').value : El('imgCoadds').value),
            'imgItime':(imgMode == 'Slave4' ? El('itimeSets').value : El('imgItime').value),
            'nodOffX':nodOffX,
            'nodOffY':nodOffY,
            'skyPattern':El('skyPattern').value,
            'skyFrames1':El('skyFrames1').value,
            'skyFrames2':El('skyFrames2').value,
            'skyLenX':skyLenX,
            'skyHgtY':skyHgtY,
            'defs':self.defs
        };
        //console.log(params);
        return params;
    };

    self.update = function () {
        self.showPosList(false);
        self.storeDefs;

        var params = self.createQstr('drawgui');
        var qry = formatGET(params);
        //El('imgResult').src='oopgui.php?'+qry;
        El('imgResult').src=self.baseurl+'/drawgui?'+qry;
    };

    self.getPCodes = function() {
        function callback(data){
            console.log('data: ', data);
            var select = El('pcodelist');
            while(select.hasChildNodes()){
                select.removeChild(select.lastChild);
            }
            codes = data['pcodes'];
            console.log(codes);
            for (var code in codes){
                var option = document.createElement('option');
                option.value = codes[code];
                option.innerHTML = codes[code];
                select.appendChild(option);
            }
        }
        params = { 'keckID':self.checkCookie()};
        console.log("params: ", params);
        ajaxCall(self.baseurl+'/getPCodes',params, callback);
    };

    self.clearFields = function() {
        El('ddfname').value = "default.ddf";
        El('imgMode').value = "Disabled";
        El('dataset').value = "<none>";
        El('object').value = "<none>";
        El('targType').value = "target";
        El('coordSys').value = 'instr';
        El('aoType').value = "NGS";
        El('lgsMode').value = "No Laser";
        El('units').value = "arcsec";
        El('pa').value = 0.0;
        El('specFilter').value = "Zbb";
        El('scale').value = "0.02";
        El('specCoadds').value  = 1.0;
        El('specItime').value = 1.476;
        El('initOffX').value = 0.0;
        El('initOffY').value = 0.0;
        El('objPattern').value = "Stare";
        El('objFrames1').value = 1.0;
        El('objFrames2').value = 1.0;
        El('objLenX').value = 0.0;
        El('objHgtY').value = 0.0;
        El('imgFilter').value = "Opn";
        El('mask').value = 'Open Circ';
        El('imgFilterSets').value = '';
        El('repeats').value = 1.0;
        El('repeatSets').value = '';
        El('imgCoadds').value = 1.0;
        El('coaddSets').value = '';
        El('imgItime').value = 2.0;
        El('itimeSets').value = '';
        El('nodOffX').value = 0.0;
        El('nodOffY').value = 0.0;
        El('skyPattern').value = "None";
        El('skyFrames1').value = 1.0;
        El('skyFrames2').value = 1.0;
        El('skyLenX').value = 0.0;
        El('skyHgtY').value = 0.0;
        self.defs = {};

        self.enableLGS();
        self.setMode();
        self.objMode();
        self.skyMode();
        self.update();
    };

    //El('imgResult').src='oopgui.php?'+formatGET(self.createQstr('drawgui'));
    El('imgResult').src=self.baseurl+'/drawgui?'+formatGET(self.createQstr('drawgui'));
    self.getPCodes();

    El('updateBt').onclick = self.update;
    El('fileList').onclick = self.showFile;
    El('showPosBtn').onclick = self.clickPosBtn;
    El('submitDefs').onclick = self.storeDefs;
    El('saveBtn').onclick = self.saveDDF;
    El('queue').onclick = self.saveDDF;
    El('saveDB').onclick = self.saveDB;
    El('loadDB').onclick = self.loadDB;
    El('ddfname').onclick = self.setDDF;
    El('loadDDF').onclick = self.getFile;
    El('file-input').onchange = self.openDDF;
    El('clear').onclick = self.clearFields;
    El('dbList').onchange = self.loadPreview;
    El('loadConfig').onclick = self.loadConfig;
    El('showFilterSets').onclick = self.clickFilterSets;
}
