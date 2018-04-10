function Example1 ()
{
    var self = this;

    function E(n) { return document.getElementById(n); }

    self.update = function () {
        function callback (val) {
            E('resultImg').src = 'image?paramL';
        }

        ajaxCall ('func1', {}, callback);
    };

    self.plot = function () {
        var L = E('paramL').value;
        var F = E('paramF').value;
        E('imgResult').src = 'getImage?paramL='+L+'&paramF='+F;
    };

    self.calculate = function () {
        function callback (val) {
            E('result').innerHTML = val['result'];
        }
        var params = {
            'paramA':E('paramA').value, 
            'paramB':E('paramB').value
            };
        ajaxCall('getResult', params, callback);
    };


    E('calculateBt').onclick = self.calculate;
    E('plotBt').onclick = self.plot;
}
