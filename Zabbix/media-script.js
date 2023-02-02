// This needs to be placed in the Zabbix GUI -> Administration -> Media types -> cstate -> Script

var cstate = {
    message: null,
    proxy: null,

    sendMessage: function() {
        var params = {
            //to-do: consider shipping useful text for use in the issue body
            //text: cstate.message,
            name: cstate.name,
            time: cstate.time,
            date: cstate.date,
            updatestatus: cstate.updatestatus,
            status: cstate.eventstatus,
            id: cstate.eventid,
            servicedescription: cstate.servicedescription,
            servicetags: cstate.servicetags,
            system: cstate.system,
            subsystems: cstate.subsystems,
            severity: cstate.severity
        },
        data,
        response,
        request = new CurlHttpRequest(),
        //to-do: move this to a Zabbix parameter
        url = 'http://127.0.0.1:8090/call';

        if (cstate.proxy) {
            request.SetProxy(cstate.proxy);
        }

        request.AddHeader('Content-Type: application/json');
        data = JSON.stringify(params);

        Zabbix.Log(4, '[cstate Webhook] params: ' + data);
        response = request.Post(url, data);
        Zabbix.Log(4, '[cstate Webhook] HTTP code: ' + request.Status());

        try {
            response = JSON.parse(response);
        }
        catch (error) {
            response = null;
        }

        if (request.Status() !== 200) {
            if (typeof response.description === 'string') {
                throw response.description;
            }
            else {
                throw 'Unknown error. Check debug log for more information.'
            }
        }
    }
}

try {
    var params = JSON.parse(value);

    if (params.HTTPProxy) {
        cstate.proxy = params.HTTPProxy;
    }

    cstate.message = params.Subject + '\n' + params.Message;
    cstate.name = params.EventName;
    cstate.time = params.EventTime;
    cstate.date = params.EventDate;
    cstate.severity = params.EventSeverity;
    cstate.updatestatus = params.EventUpdateStatus;
    cstate.eventstatus = params.EventStatus;
    cstate.eventid = params.EventId;
    cstate.servicedescription = params.ServiceDescription;
    cstate.servicetags = params.ServiceTags;
    cstate.system = params.cstatesystem;
    cstate.subsystems = params.cstatesubsystems;
    cstate.sendMessage();

    return 'OK';
}
catch (error) {
    Zabbix.Log(4, '[cstate Webhook] notification failed: ' + error);
    throw 'Sending failed: ' + error + '.';
}
