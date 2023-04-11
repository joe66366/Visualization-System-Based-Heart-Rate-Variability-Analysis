async function get_hrv(){
    var response1 = await eel.hrv_info1()();
    response1 = JSON.parse(response1);
    var output1 = '';
    for (var key in response1){
        output1 += key + ": " + response1[key] + "\n" ;
    }
    document.getElementById('hrv_feature1').innerText = output1


    var response2 = await eel.hrv_info2()();
    response2 = JSON.parse(response2);
    var output2 = '';
    for (var key in response2){
        output2 += key + ": " + response2[key] + "\n" ;
    }
    document.getElementById('hrv_feature2').innerText = output2
}
