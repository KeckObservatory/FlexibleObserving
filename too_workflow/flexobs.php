<html>
    <head>
        <title>Submit ToO</title>
        <link rel='stylesheet' type='text/css' href='http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css'/>
        <script src="jquery.min"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.9.2/jquery-ui.min.js"></script>
    </head>
    <body>
<?php
    function getInstruments(){
        $url = "https://www.keck.hawaii.edu/software/db_api/telSchedule.php?cmd=getToO&semester=2018A&projcode=U020";
        $res = file_get_contents($url);
        return $res;
    }

    function getMonth(){
    }

    function getInstrConfig(){
    }

    function getTargetList(){
    }
?>
    <script >
        $(function(){
            $('#projcode').change(function(){
                if($(this).val() != ""){
                    $('#Instrument').show();
                } else {
                    $('#Instrument').hide();
                }
            });
        });

        function jsInstruments(id){
        };

        $(function(){
            $('#instrument').change(function(){
                if($(this).val() != ""){
                    $('#Night').show();
                } else {
                    $('#Night').hide();
                }
            });
        });

        function jsMonth(){
        };

        $(function(){
            $('#requestedNight').datepicker();
            $('#requestedNight').change(function(){
                if($(this).val() != ""){
                    $('#InstrConfig').show();
                } else {
                    $('#InstrConfig').hide();
                }
            });
        });

        function jsInstrConfig(){
        };

        $(function(){
            $('#instrconfig').change(function(){
                if($(this).val() != ""){
                    $('#TargetList').show();
                } else {
                    $('#TargetList').hide();
                }
            });
        });

        function jsTargetList(){
        };

        $(function(){
            $('#targetlist').change(function(){
                if($(this).val() != ""){
                    $('#Sequence').show();
                } else {
                    $('#Sequence').hide();
                }
            });
        });
        $(function(){
            $('#sequence').change(function(){
                if($(this).val() != ""){
                    $('#Trigger').show();
                } else {
                    $('#Trigger').hide();
                }
            });
        });
    </script>
        <div id="ProjCode">
            Project Code:
            <select name="projcode" id="projcode" onchange="jsInstruments(this.value);">
                <option value="">Select...</option>
                <option value="2018A_U020">Supernova progenitors with Keck and the Global Supernova Project</option>
                <option value="2018A_&030">To: NIRC2 Imaging of Volcanic Outbursts on Io</option>
            </select>
        </div>
        <div id="Instrument" style="display:none">
            Instrument:
            <select name="instrument" id="instrument">
                <option value="">Select...</option>
                <option value="1">HIRESr</option>
            </select>
        </div>
        <div id="Night" style="display:none">
            Night:
            <input type='text' id="requestedNight">
        </div>
        <div id="InstrConfig" style="display:none">
            Instrument Configuration:
            <select name="instrconfig" id="instrconfig">
                <option value="">Select...</option>
                <option value="1">This Config</option>
            </select>
        </div>
        <div id="TargetList" style="display:none">
            Target List:
            <select name="targetlist" id="targetlist">
                <option value="">Select...</option>
                <option value="1">That Target Over There</option>
            </select>
        </div>
        <div id="Sequence" style="display:none">
            Sequence:
            <form name="sequence" id="sequence">
                Number: <input type="text" id="Number" name="Number">
                Pattern: <input type="text" id="Pattern" name="Pattern">
                Time: <input type="text" id="Time" name="Time">
            </form>
        </div>
        <div id="Trigger" style="display:none">
            <form id="trigger" method="post">
                <input type="submit" value="Trigger ToO">
            </form>
        </div>
    </body>
</html>
