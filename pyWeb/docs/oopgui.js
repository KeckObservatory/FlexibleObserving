function Oopgui(){
    var self = this;
    self.keckID = '';
    self.userdefs = {};
    self.offdefs = {
        Stare:[[0,0]],
        Box4:[[0,0], [1,0], [1,-1], [0,-1]],
        Box5:[[0,0],[-1,1],[1,1],[1,-1],[-1,-1]],
        Box9:[[0,0],[-1,1],[-1,-1],[1,1],[1,-1],[-1,0],[1,0],[0,1],[0,-1]]
    };

    function El(id) { return document.getElementById(id); };

    function formatGET(vars) {
        var qry = "";
        for (val in vars){
            qry += val + "=" + vars[val] + "&";
        }
        qry = qry.slice(0,qry.length-1);
        return qry;
    };

    function openDDF() {
        var file = e.target.files[0];
        if(!file) {
            return;
        }
        var reader = new FileReader();
        reader.onload = function(e) {
        }
    };

    self.saveDDF = function() {
        function callback(data){
            console.log("In the callback");
        }

        var params = self.createQstr();
        ajaxCall ('save_to_file', params, callback);
    };

    self.saveDB = function() {
        function callback(data){
            console.log('saved to database');
        }

        var params = self.createQstr();
        ajaxCall('save_to_db', params, callback);
    };

    self.setCookie = function(key, val, exdays){
        var d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        var expires = 'expires=' + d.toGMTString();
        document.cookie = key + '+' + val + ';' + expires + ';path=/';
    };

    self.checkCookie = function(){
        var keckid = self.getKeckID();
        if (keckid != '' && keckid != undefined) return keckid;
        else { // Add logic here to log into obs page
            keckid = prompt("Please enter a keckid:","");
            if (keckid != '' && keckid != null) {
                self.setCookie('keckID', keckid, 10);
            }
        }
        return keckid;
    };

    self.getKeckID = function(){
        var allcookies = document.cookie;
        var cookies = allcookies.split(';');
        for (var i=0; i < cookies.length; i++){
            name = cookies[i].split('+')[0];
            value = cookies[i].split('+')[1];
            if (name == 'keckID') return value;
        }
        return '';
    };

    self.showFile = function(){
        El("loadfile").classList.toggle("show");
    };

    self.showQueue = function(){
        El('queue').classList.toggle('show');
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

    self.checkFilter = function(){
        var filter = El('specFilter').value;
        var scale = El('scale');
        switch (filter){
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

    self.setMode = function (){
        var mode = El('imgMode');
        if (mode.value == 'Disabled'){
            El('specFilter').disabled = false;
            El('scale').disabled = false;
            El('specCoadds').disabled = false;
            El('specItime').disabled = false;
            El('imgFilter').disabled = true;
            El('repeats').disabled = true;
            El('imgCoadds').disabled = true;
            El('imgItime').disabled = true;
            El('spec').style.backgroundColor = 'lightblue';
            El('imag').style.backgroundColor = '#ffa';
            El('both').style.backgroundColor = '#ffa';
        }
        else if (mode.value == 'Independent'){
            El('specFilter').disabled = true;
            El('scale').disabled = true;
            El('specCoadds').disabled = true;
            El('specItime').disabled = true;
            El('imgFilter').disabled = false;
            El('repeats').disabled = false;
            El('imgCoadds').disabled = false;
            El('imgItime').disabled = false;
            El('spec').style.backgroundColor = '#ffa';
            El('imag').style.backgroundColor = 'lightblue';
            El('both').style.backgroundColor = '#ffa';
        }
        else if (mode.value == 'Slave4') {
            El('specFilter').disabled = false;
            El('scale').disabled = false;
            El('specCoadds').disabled = false;
            El('specItime').disabled = false;
            El('imgFilter').disabled = true;
            El('repeats').disabled = true;
            El('imgCoadds').disabled = true;
            El('imgItime').disabled = true;
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
            El('repeats').disabled = false;
            El('imgCoadds').disabled = false;
            El('imgItime').disabled = false;
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

    self.showPosList = function (){
        var userdefs = El('userdefs');
        var numObjFrames;
        var objPattern = El('objPattern').value;
        if (objPattern=='None') numObjFrames = 0;
        else numObjFrames = El('objFrames1').value;
        var numSkyFrames;
        var skyPattern = El('skyPattern').value;
        if (skyPattern=='None') numSkyFrames = 0;
        else numSkyFrames = El('skyFrames1').value;
        var count = 1;
        if (userdefs.style.display == 'none') userdefs.style.display = 'block';
        else userdefs.style.display = 'none';
        var initOffX = parseFloat(El('initOffX').value);
        var initOffY = parseFloat(El('initOffY').value);
        var objLenX = parseFloat(El('objLenX').value);
        var objHgtY = parseFloat(El('objHgtY').value);
        var nodOffX = parseFloat(El('nodOffX').value);
        var nodOffY = parseFloat(El('nodOffY').value);
        var skyLenX = parseFloat(El('skyLenX').value);
        var skyHgtY = parseFloat(El('skyHgtY').value);

        // Remove any previous nodes
        var table = El('defs');
        while(table.hasChildNodes()){
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
        for(i=0; i<numObjFrames; i++){
            row = document.createElement('tr');
            cell = document.createElement('td');
            cell.innerHTML = count;
            row.appendChild(cell);
            cell = document.createElement('td');
            var value = 0;
            if(objPattern!='User Defined'){
                value = self.offdefs[objPattern][i][0]+initOffX+objLenX;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            if(objPattern!='User Defined'){
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

        for(i=0; i<numSkyFrames; i++){
            row = document.createElement('tr');
            cell = document.createElement('td');
            cell.innerHTML = count;
            row.appendChild(cell);
            cell = document.createElement('td');
            var value = 0;
            if(skyPattern != 'User Defined'){
                value = self.offdefs[skyPattern][i][0]+initOffX+nodOffX+skyLenX;
                cell.innerHTML = '<input type="text" value='+value+' disabled>';
            }
            else cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            if(skyPattern!='User Defined'){
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

    self.storeDefs = function(){
        var table = El('defs');
        var objPattern = El('objPattern').value;
        var skyPattern = El('skyPattern').value;
        var numrows = parseFloat(El('objFrames1').value)
            + parseFloat(El('skyFrames1').value) + 1;
        var t = [];
        var i = 1;
        if(objPattern == "Stare") i+=1;
        else if (objPattern == "Box4") i+=4;
        else if (objPattern == "Box5") i+=5;
        else if (objPattern == "Box9") i+=9;
        if(skyPattern == "Stare") numrows-=1;
        else if(skyPattern == "Box4") numrows-=4;
        else if(skyPattern == "Box5") numrows-=5;
        else if(skyPattern == "Box9") numrows-=9;
        for(i; row=table.rows[i]; i++){
            var r = [];
            r.push(row.cells[1].lastChild.value);
            r.push(row.cells[2].lastChild.value);
            if(row.cells[3].lastChild.checked==true)
                r.push(true);
            else r.push(false);
            t.push(r);
            if(i+1==numrows) break;
        }

        self.defs = t;
        console.log(self.defs);
        El('userdefs').style.display = 'None';
    };

    self.createQstr = function(){
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

        if (typeof(self.defs) != typeof({})) self.defs = {};

        var params = {
            'keckID':self.checkCookie(),
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
            'imgFilter':El('imgFilter').value,
            'repeats':El('repeats').value,
            'imgCoadds':El('imgCoadds').value,
            'imgItime':El('imgItime').value,
            'nodOffX':nodOffX,
            'nodOffY':nodOffY,
            'skyPattern':El('skyPattern').value,
            'skyFrames1':El('skyFrames1').value,
            'skyFrames2':El('skyFrames2').value,
            'skyLenX':skyLenX,
            'skyHgtY':skyHgtY,
            'defs':self.defs
        };
        console.log(params);
        return params;
    };

    self.update = function (){
        function callback(data){
            console.log("In the callback");
            El('imgResult').src='data:image/png;base64,' + data;
        }

        var params = self.createQstr();

        var qry = formatGET(params);
        El('imgResult').src='drawgui?'+qry;
        //ajaxCall ('drawgui', params, callback);
    };

    El('updateBt').onclick = self.update;
    El('fileList').onclick = self.showFile;
    El('queueList').onclick = self.showQueue;
    El('showPosBtn').onclick = self.showPosList;
    El('submitDefs').onclick = self.storeDefs;
    El('saveBtn').onclick = self.saveDDF;
    El('saveDB').onclick = self.saveDB;
}
