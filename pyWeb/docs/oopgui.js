function Oopgui(){
    var self = this;

    function El(id) { return document.getElementById(id); }

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
            El('objHgtY').disabled = false;t 
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

    self.update = function () {
        function callback(data){
            //El('imgResult').src='data:image/png;base64,' + data;
            El('imgResult').src='myimg.jpg';
        }
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
            'objLenX':El('objLenX').value,
            'objHgtY':El('objHgtY').value,
            'imgFilter':El('imgFilter').value,
            'repeats':El('repeats').value,
            'imgCoadds':El('imgCoadds').value,
            'imgItime':El('imgItime').value,
            'nodOffX':El('nodOffX').value,
            'nodOffY':El('nodOffY').value,
            'skyPattern':El('skyPattern').value,
            'skyFrames':El('skyFrames').value,
            'skyLenX':El('skyLenX').value,
            'skyHgtY':El('skyHgtY').value
        };

        ajaxCall ('drawgui', params, callback);
    };

    self.echo = function () {
        function callback (data) {
            El('mypara').innerHTML = data['result'];
        }
        ajaxCall('echothis', {}, callback);
    };

    El('updateBt').onclick = self.update;
    El('echoBt').onclick = self.echo;

}
