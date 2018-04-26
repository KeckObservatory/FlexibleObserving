function Oopgui(){
    var self = this;

    function El(id) { return document.getElementById(id); }

    function formatGET(vars) {
        var qry = "";
        for (val in vars){
            qry += val + "=" + vars[val] + "&";
        }
        qry = qry.slice(0,qry.length-1);
        return qry;
    }

    function openDDF() {
        var file = e.target.files[0];
        if(!file) {
            return;
        }
        var reader = new FileReader();
        reader.onload = function(e) {
        }
    }

    self.showFile = function(){
        El("loadfile").classList.toggle("show");
    }

    self.showQueue = function(){
        El('queue').classList.toggle('show');
    }

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
    }

    self.enableLGS = function () {
        var aomode = El('aoType');
        if (aomode.value == 'LGS') {
            El('lgsMode').disabled = false;
        }
        else {
            El('lgsMode').disabled = true;
        }
    };

    self.objMode = function () {
        var pattern = El('objPattern');
        if (pattern.value == "None") {
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            El('objFrames').disabled = true;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            El('objOffLenStepX').innerHTML = "None: ";
            El('objOffHgtStepY').innerHTML = "None: ";
        }
        else if (pattern.value == "Stare") {
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            var objFrames = El('objFrames');
            objFrames.disabled = true;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            objFrames.value = 1;
            El('objOffLenStepX').innerHTML = "Unused: ";
            El('objOffHgtStepY').innerHTML = "Unused: ";
        }
        else if (pattern.value== "Statistical Dither") {
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            El('objFrames').disabled = false;
            El('objLenX').disabled = false;
            El('objHgtY').disabled = false;
            El('objOffLenStepX').innerHTML = 'Region Length: ';
            El('objOffHgtStepY').innerHTML = 'Region Height: ';
        }
        else if (pattern.value == "Raster Scan") {
            El('objFrames').disabled = false;
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
            El('objFrames').disabled = false;
            El('objLenX').disabled = true;
            El('objHgtY').disabled = true;
            El('objOffLenStepX').innerHTML = 'Unused: ';
            El('objOffHgtStepY').innerHTML = 'Unused: ';
        }
        else {
            El('objRaster').style.display = 'none';
            El('objFramesCell').setAttribute("colspan", 3);
            var frames = El('objFrames');
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
            El('nodOffX').disabled = true;
            El('nodOffY').disabled = true;
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
            El('skyFrames').disabled = true;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            El('skyOffLenStepX').innerHTML = "None: ";
            El('skyOffHgtStepY').innerHTML = "None: ";
        }
        else if (pattern.value == "Stare") {
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
            var skyFrames = El('skyFrames');
            skyFrames.disabled = true;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            skyFrames.value = 1;
            El('skyOffLenStepX').innerHTML = "Unused: ";
            El('skyOffHgtStepY').innerHTML = "Unused: ";
        }
        else if (pattern.value== "Statistical Dither") {
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyFrames').disabled = false;
            El('skyLenX').disabled = false;
            El('skyHgtY').disabled = false;
            El('skyOffLenStepX').innerHTML = 'Region Length: ';
            El('skyOffHgtStepY').innerHTML = 'Region Height: ';
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
        }
        else if (pattern.value == "Raster Scan") {
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            El('skyFrames').disabled = false;
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
            El('skyFrames').disabled = false;
            El('skyLenX').disabled = true;
            El('skyHgtY').disabled = true;
            El('skyOffLenStepX').innerHTML = 'Unused: ';
            El('skyOffHgtStepY').innerHTML = 'Unused: ';
            El('skyRaster').style.display = 'none';
            El('skyFramesCell').setAttribute("colspan", 3);
        }
        else {
            El('nodOffX').disabled = false;
            El('nodOffY').disabled = false;
            var frames = El('skyFrames');
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
        var numObjFrames = El('objFrames').value;
        var numSkyFrames = El('skyFrames').value;
        var count = 1;
        if (userdefs.style.display == 'none') userdefs.style.display = 'block';
        else userdefs.style.display = 'none';

        // Remove any previous nodes
        while(userdefs.hasChildNodes()){
            userdefs.removeChild(userdefs.lastChild);
        }

        // Append new child nodes
        var table = document.createElement('table');
        table.id = 'defs';
        userdefs.appendChild(table);
        table = El('defs');
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = '#';
        cell = row.insertCell(1);
        cell.innerHTML = 'Xoff (")';
        cell = row.insertCell(2);
        cell.innerHTML = 'Yoff (")';
        cell = row.insertCell(3);
        cell.innerHTML = 'Sky?';

        for(i=0; i<numObjFrames; i++){
            row = document.createElement('tr');
            cell = document.createElement('td');
            cell.innerHTML = count;
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = "<input type='checkbox'>";
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
            cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = '<input type="text">';
            row.appendChild(cell);
            cell = document.createElement('td');
            cell.innerHTML = "<input type='checkbox' checked='checked'>";
            row.appendChild(cell);
            table.appendChild(row);
            count += 1;
        }
        var submit = document.createElement('button');
        submit.id = 'submitdefs';
        submit.innerHTML = 'Submit';
        userdefs.appendChild(submit);
    }

    self.update = function (){
        function callback(data){
            console.log("In the callback");
            El('imgResult').src='data:image/png;base64,' + data;
        }

        // Check for disabled boxes
        var objFrames = El('objFrames');
        var objLenX = El('objLenX');
        var objHgtY = El('objHgtY');
        var nodOffX = El('nodOffX');
        var nodOffY = El('nodOffY');
        var skyFrames = El('skyFrames');
        var skyLenX = El('skyLenX');
        var skyHgtY = El('skyHgtY');

        if (objLenX.disabled == true) objLenX = 0.0;
        else objLenX = objLenX.value;
        if (objHgtY.disabled == true) objHgtY = 0.0;
        else objHgtY = objHgtY.value;
        if (nodOffX.disabled == true) nodOffX = 0.0;
        else nodOffX = nodOffX.value;
        if (nodOffY.disabled == true) nodOffY = 0.0;
        else nodOffY = nodOffY.value;
        if (skyLenX.disabled == true) skyLenX = 0.0;
        else skyLenX = skyLenX.value;
        if (skyHgtY.disabled == true) skyHgtY = 0.0;
        else skyHgtY = skyHgtY.value;

        var params = {
            'imgMode':El('imgMode').value,
            'dataset':El('dataset').value,
            'object':El('object').value,
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
            'objFrames':El('objFrames').value,
            'objLenX':objLenX,
            'objHgtY':objHgtY,
            'imgFilter':El('imgFilter').value,
            'repeats':El('repeats').value,
            'imgCoadds':El('imgCoadds').value,
            'imgItime':El('imgItime').value,
            'nodOffX':nodOffX,
            'nodOffY':nodOffY,
            'skyPattern':El('skyPattern').value,
            'skyFrames':El('skyFrames').value,
            'skyLenX':skyLenX,
            'skyHgtY':skyHgtY//,
            //'userdefs':El('userdefs').value
        };

        qry = formatGET(params);
        El('imgResult').src='drawgui?'+qry;
        //ajaxCall ('drawgui', params, callback);
    };

    El('updateBt').onclick = self.update;
    El('fileList').onclick = self.showFile;
    El('queueList').onclick = self.showQueue;
    El('showPosBtn').onclick = self.showPosList;

}
