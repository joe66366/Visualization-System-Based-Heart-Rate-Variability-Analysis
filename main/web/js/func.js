let array_hrv=[];
//儲存成Object
const update_hrv = value =>{
    let hrv_js={}
    let tdf=['mean_nni','sdnn','sdsd','nni_50','pnni_50','nni_20','pnni_20','rmssd','median_nni','range_nni',
    'cvsd','cvnni','mean_hr','max_hr','min_hr','std_hr'];
    let fdf=['lf','hf','lf_hf_ratio','lfnu','hfnu','total_power','vlf'];
    let nl=['csi','cvi','Modified_csi','sampen','sd1','sd2','ratio_sd2_sd1'];
    tdf.forEach(element =>{
        document.getElementById(element).innerText = value['time_domain_features'][element];
        hrv_js[element]=value['time_domain_features'][element];
    });
    fdf.forEach(element =>{
        document.getElementById(element).innerText = value['frequency_domain_features'][element];
        hrv_js[element]=value['frequency_domain_features'][element];
    });
    nl.forEach(element =>{
        document.getElementById(element).innerText = value['non_Linear'][element];
        hrv_js[element]=value['non_Linear'][element];
    });
    return hrv_js;
}
//data 格式需為Array
const buildData = (data,patientID) => {

    return new Promise((resolve, reject) => {

    // 最後所有的資料會存在這
        let arrayData = [];
        
        // 取 data 的第一個 Object 的 key 當表頭
        let arrayTitle = Object.keys(data[0]);
        arrayData.push(arrayTitle);
        // 取出每一個 Object 裡的 value，push 進新的 Array 裡
        Array.prototype.forEach.call(data, d => {
            let items = [];
            Array.prototype.forEach.call(arrayTitle, title => {
            let item = d[title] || '';
            items.push(item);
            });
            arrayData.push(items);
        })
        arrayData[0].unshift("patientID");
        arrayData[1].unshift(patientID);
        resolve(arrayData);
    })
}

const downloadCSV = (data,patID) => {
    let csvContent = '';
    Array.prototype.forEach.call(data, d => {
        let dataString = d.join(',') + '\n';
        csvContent += dataString;
    })

    // 下載的檔案名稱
    let fileName = patID + '.csv';

    // 建立一個 a，並點擊它
    let link = document.createElement('a');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,%EF%BB%BF' + encodeURI(csvContent));
    link.setAttribute('download', fileName);
    link.click();
}

const doDownload =data=>{
    if(data!=""){
        try {
            buildData(array_hrv,data)
                .then(res =>downloadCSV(res,data))
                .catch(err => window.alert(err));
        } 
        catch(err) {
            window.alert(err)
        } 
    }
    else{
        alert("請輸入病歷號")
    }
}
// 非同步確保資料傳遞
const doWrite = async(data)=>{
    if(data!=""){
        let prm_hrv=buildData(array_hrv,data);
        let res_hrv= await readPromise(prm_hrv);
        let write= await eel.write_csv(res_hrv)();
        if(write=="success"){
            alert("儲存成功!")
        }
        else{
            alert("失敗!")
        }
    }
    else{
        alert("請輸入病歷號")
    }
}

// 讀取Promise格式
const readPromise = async(data) =>{
    let resdata
    resdata = await data.then(res=>{return res[1];});
    return resdata;

}

async function select(nrow, choosefile){
    var value = await eel.selectFolder(nrow, choosefile)();
    // init plotly_div
    document.querySelector('#plotly_div').innerHTML = ''
    // init selector
    document.getElementById("time").hidden = false;
    document.getElementById("analysis").hidden=false;
    document.getElementById("download").hidden=false;

    var tmp = JSON.parse(value)["ecg"];
    var range = [...Array(JSON.parse(tmp[0]).length).keys()];
    array_hrv=[];
    page = 0;
    move_PLETH = 200;
    move_RESP = 250;
    var layout = {
        width: nrow*0.6,
		height: 200,
        yaxis:  {visible: false},
		margin: {
            l: 30,
			t: 30,
			b: 20
        }
	};

    tmp.forEach(function(item){
        page += 1;
        // append child plotly div
        var node = document.createElement('div');
        node.setAttribute("id", "myDiv"+page);
        node.setAttribute("style", "overflow:auto");
        document.querySelector('#plotly_div').appendChild(node);
        item = JSON.parse(item);
        II = [];
        ABP = [];
        PLETH = [];
        RESP = [];
        item.forEach(function(obj){
            II.push(obj['II']);
            ABP.push(obj['ABP']);
            PLETH.push(obj['PLETH'] + move_PLETH);
            RESP.push(obj['RESP'] + move_RESP);
        })
        var II_curve = {
            x: range,
            y: II,
            name: 'II',
            type: 'scatter',
        };
        var PLETH_curve = {
            x: range,
            y: PLETH,
            name: 'PLETH',
            type: 'scatter',
            customdata: RESP.map(num => num - move_PLETH),
            hovertemplate:  '%{customdata}'
        };
        var RESP_curve = {
            x: range,
            y: RESP,
            name: 'RESP',
            type: 'scatter',
            customdata: RESP.map(num => num - move_RESP),
            hovertemplate: '%{customdata}'
        };
        id = 'myDiv' + page
        Plotly.newPlot(id, [II_curve, PLETH_curve, RESP_curve], layout);
    })
	var hrvdata=JSON.parse(value);
    // 更新前端數據
	var hrv_js = update_hrv(hrvdata);
    array_hrv.push(hrv_js);

}
