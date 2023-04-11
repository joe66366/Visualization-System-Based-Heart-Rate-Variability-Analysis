const average = arr => arr.reduce( ( p, c ) => p + c, 0 ) / arr.length;

function update_hrv(value){
    if (value['time_domain_features']['sdnn'] != null) {
        document.getElementById('sdnn').innerText = value['time_domain_features']['sdnn'];
    }
    if (value['time_domain_features']['nni'] != null) {
        document.getElementById('nni').innerText = value['time_domain_features']['nni'];
    }
    
    if (value['time_domain_features']['pnni'] != null) {
        document.getElementById('pnni').innerText = value['time_domain_features']['pnni'];
    }
    if (value['time_domain_features']['rmssd'] != null) {
        document.getElementById('rmssd').innerText = value['time_domain_features']['rmssd'];
    }
    if (value['time_domain_features']['range_nni'] != null) {
        document.getElementById('range_nni').innerText = value['time_domain_features']['range_nni'];
    }

    if (value['frequency_domain_features']['lf'] != null) {
        document.getElementById('lf').innerText = value['frequency_domain_features']['lf'];
    }
    if (value['frequency_domain_features']['hf'] != null) {
        document.getElementById('hf').innerText = value['frequency_domain_features']['hf'];
    }
    if (value['frequency_domain_features']['lf_hf_ratio'] != null) {
        document.getElementById('lf_hf_ratio').innerText = value['frequency_domain_features']['lf_hf_ratio'];
    }
    if (value['frequency_domain_features']['lfnu'] != null) {
        document.getElementById('lfnu').innerText = value['frequency_domain_features']['lfnu'];
    }
    if (value['frequency_domain_features']['hfnu'] != null) {
        document.getElementById('hfnu').innerText = value['frequency_domain_features']['hfnu'];
    }

    if (value['non_Linear']['csi'] != null) {
        document.getElementById('csi').innerText = value['non_Linear']['csi'];
    }
    if (value['non_Linear']['cvi'] != null) {
        document.getElementById('cvi').innerText = value['non_Linear']['cvi'];
    }
    if (value['non_Linear']['Modified_csi'] != null) {
        document.getElementById('Modified_csi').innerText = value['non_Linear']['Modified_csi'];
    }
}

var ecg_layout = {
    title: {
        text: 'ecg',
        font: {
            color: '#3BFF3B'
        }
    },
    xaxis: {
        dtick: 40
    },
    yaxis: {
        titlefont: {
            size: 14, 
            color: 'rgb(107, 107, 107)'
        }, 
        tickfont: {
            size: 14, 
            color: "rgb(107, 107, 107)"
        }
    },
    plot_bgcolor:"#000000",
    paper_bgcolor:"#000000",
    height: 150,
    margin: {
        l: 30,
        t: 30,
        b: 20
    }
};

var pleth_layout = {
    title: {
        text: 'pleth',
        font: {
            color: '#AFEEEE'
        }
    },
    xaxis: {
        dtick: 40
    },
    yaxis: {
        titlefont: {
            size: 14, 
            color: 'rgb(107, 107, 107)'
        }, 
        tickfont: {
            size: 14, 
            color: "rgb(107, 107, 107)"
        }
    },
    plot_bgcolor:"#000000",
    paper_bgcolor:"#000000",
    height: 150,
    margin: {
        l: 30,
        t: 30,
        b: 20
    }
};

var resp_layout = {
    title: {
        text: 'resp',
        font: {
            color: '#F8F8FF'
        }
    },
    xaxis: {
        dtick: 40
    },
    yaxis: {
        titlefont: {
            size: 14, 
            color: 'rgb(107, 107, 107)'
        }, 
        tickfont: {
            size: 14, 
            color: "rgb(107, 107, 107)"
        }
    },
    plot_bgcolor:"#000000",
    paper_bgcolor:"#000000",
    mode: 'lines',
    height: 150,
    margin: {
        l: 30,
        t: 30,
        b: 20
    }
};
var config = {responsive: true}
async function start_realtime(){
    console.log('init plotly')
    // 不能傳給app.py，因為consumer是同步的，如果沒有消費到一定條件，會卡住app.py的資源
    var value = await eel.start_realtime()();
    value = JSON.parse(value);
    var trace1 = {
            y: value['ecg'],
            type: 'line'
    };
    var trace2 = {
        y: value['pleth'],
        type: 'line'
    };
    var trace3 = {
        y: value['resp'],
        type: 'line'
    };
    var data = [{
        trace1, 
        line: { color: '#3BFF3B'}
    }];
    var data2 = [{
        trace2,
        line: { color: '#AFEEEE'}
    }];
    var data3 = [{
        trace3,
        line: { color: '#F8F8FF'}
    }];

    Plotly.newPlot('myDiv1', data, ecg_layout, config);
    Plotly.newPlot('myDiv2', data2, pleth_layout, config);
    Plotly.newPlot('myDiv3', data3, resp_layout, config);
};
start_realtime();
async function adjustRealtime_value(){
    console.log('adjusting');
    var value = await eel.start_realtime()();
    value = JSON.parse(value);
    document.getElementById('hr_min').innerText = Math.min(...value['ecg']);
    document.getElementById('hr_max').innerText = Math.max(...value['ecg']);
    document.getElementById('hr_avg').innerText = Math.floor(average(value['ecg']));
    
    document.getElementById('spo2_min').innerText = Math.min(...value['pleth']);
    document.getElementById('spo2_max').innerText = Math.max(...value['pleth']);
    document.getElementById('spo2_avg').innerText = Math.floor(average(value['pleth']));
    
    document.getElementById('rr_min').innerText = Math.min(...value['resp']);
    document.getElementById('rr_max').innerText = Math.max(...value['resp']);
    document.getElementById('rr_avg').innerText = Math.floor(average(value['resp']));
    
    // hrv information
    update_hrv(value);
    
    Plotly.restyle('myDiv1', 'y', [value['ecg']], ecg_layout, config);
    Plotly.restyle('myDiv2', 'y', [value['pleth']], pleth_layout, config);
    Plotly.restyle('myDiv3', 'y', [value['resp']], resp_layout, config);
}

function interval(func, wait){
    var interv = function(){
      func.call(null);
      setTimeout(interv, wait);
    };
    setTimeout(interv, wait);
}
  
interval(adjustRealtime_value, 1000);