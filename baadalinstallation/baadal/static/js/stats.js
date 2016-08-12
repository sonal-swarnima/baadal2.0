/**
 * Created by Harsh on 29-05-2016.
 */

function calculateCPUPercent(stats) {
    // Same algorithm the official client uses: https://github.com/docker/docker/blob/master/api/client/stats.go#L195-L208
    var prevCpu = stats.precpu_stats;
    var curCpu = stats.cpu_stats;

    var cpuPercent = 0.0;

    // calculate the change for the cpu usage of the container in between readings
    var cpuDelta = curCpu.cpu_usage.total_usage - prevCpu.cpu_usage.total_usage;
    // calculate the change for the entire system between readings
    var systemDelta = curCpu.system_cpu_usage - prevCpu.system_cpu_usage;

    if (systemDelta > 0.0 && cpuDelta > 0.0) {
        cpuPercent = (cpuDelta / systemDelta) * curCpu.cpu_usage.percpu_usage.length * 100.0;
    }
    return cpuPercent;
}
var mychart;
var mycharttype;
var cpuChart= [];
var memoryChart =[];
var readnetworkChart = [];
var writenetworkChart =[];
var networkName;
var myInterval;
var difference =true;
function updateCpuChart(data,mychart) {
    if(cpuChart.length >15){
        cpuChart.shift();
    }
    cpuChart.push({y :calculateCPUPercent(data), x:  new Date(data.read).getTime()} );
    mychart.render();
    //cpuChart.pop();
}

function updateMemoryChart(data,mychart) {
    if(memoryChart.length >15){
        memoryChart.shift();
    }
    memoryChart.push({y :data.memory_stats.usage, x:  new Date(data.read).getTime()});

    mychart.render();
}
var lastRxBytes = 0, lastTxBytes = 0;
function updateNetworkChart(data,mychart) {

    if(readnetworkChart.length >15){
        readnetworkChart.shift();
    }
    if(writenetworkChart.length >15){
        writenetworkChart.shift();
    }
    if (data.networks) {
        networkName = Object.keys(data.networks)[0];
        data.network = data.networks[networkName];
    }
    var rxBytes =0;
    var txBytes = 0;
    if (lastRxBytes !== 0 || lastTxBytes !== 0) {
        // These will be zero on first call, ignore to prevent large graph spike
        rxBytes = data.network.rx_bytes - lastRxBytes;
        txBytes = data.network.tx_bytes - lastTxBytes;
    }

    lastRxBytes = data.network.rx_bytes;
    lastTxBytes = data.network.tx_bytes;
    if(!difference){
        readnetworkChart.push({y :data.network.rx_bytes, x:  new Date(data.read).getTime()});
        writenetworkChart.push({y :data.network.tx_bytes, x:  new Date(data.read).getTime()});
    }
    else{
        readnetworkChart.push({y :rxBytes, x:  new Date(data.read).getTime()});
        writenetworkChart.push({y :txBytes, x:  new Date(data.read).getTime()});
    }

    mychart.render();
}

function updatestats(data){
    
            updateCpuChart(data,mycharts[0]);
        
        
            updateMemoryChart(data,mycharts[1]);
        
            updateNetworkChart(data,mycharts[2]);
        
    

}
function refreshcharts(){
    mychart = null;
     mycharttype = 1;
     cpuChart= [];
     memoryChart =[];
     readnetworkChart = [];
    writenetworkChart =[];
     myInterval = null;
}
function plotcharts(id,charts,charttype){
    mycharts = charts;
    mycharttype = charttype;
    
        
            charts[0].options.data[0].dataPoints = cpuChart;
        
            charts[1].options.data[0].dataPoints = memoryChart;
	     charts[1].options.axisY= {valueFormatString : "#M,,."};
        
            charts[2].options.data[0].dataPoints = readnetworkChart;
            charts[2].options.data[0].color= "rgba(255,12,32,.5)",
            charts[2].options.data[1] ={};
            charts[2].options.data[1].type ="area";
            charts[2].options.data[1].xValueType ="dateTime";
            charts[2].options.data[1].color= "rgba(0,135,147,.3)",
            charts[2].options.data[1].dataPoints = writenetworkChart;

        
    
    if(myInterval){
        clearInterval(myInterval);
    }
    getstats(id,updatestats)
    myInterval = setInterval(function(){getstats(id,updatestats)}, 15000);
}
