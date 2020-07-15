//Import population data
function myFunc() {
    return popData
}
//Log to make sure data is read in properly
console.log(popData);
//Sort population data from largest to smallest
var sortedpops = popData.sort((b, a) => b.count - a.count);

//Store data being plotted and style to 'data'
var data = [
    {
        y: ["Maya ","Rey ","Lynn ","Claire ","Dan "],  
        x: [sortedpops[0].count,sortedpops[1].count,sortedpops[2].count,sortedpops[3].count,sortedpops[4].count],
        type: "bar",
        orientation: 'h',
        marker: {
            color: 'rgba(0,117,201,.8)',
            line: {
                color: 'rgb(0,74,152)',
                width: 2
            }
        }
    }
];

//Store layout
var layout = {
    title: "Population",
    xaxis: { title: "Individuals"},
    yaxis: {
        tickfont: {
        size: 18,
        }
    }
};
            
// Plot the chart to a div tag with id "plot"
Plotly.newPlot("plot", data, layout);

//Avg engagements
function myFunc() {
    return avg_engage
}

var data2 = [
    {
      y: [avg_engage[3].persona,avg_engage[4].persona,avg_engage[2].persona,avg_engage[0].persona,avg_engage[1].persona],  
      x: [avg_engage[3].engagement,avg_engage[4].engagement,avg_engage[2].engagement,avg_engage[0].engagement,avg_engage[1].engagement],
      type: "bar",
      orientation: 'h',
      marker: {
        color: 'rgba(0,117,201,.8)',
        line: {
          color: 'rgb(0,74,152)',
          width: 2
        }
      }
    }
  ];
  
  var layout = {
    title: "Average Engagements Per Individual",
    xaxis: { title: "Engagements"},
    yaxis: {
      showticklabels: false
    }
  };
 
  Plotly.newPlot("plot2", data2, layout)

//Engagement type breakdown

function myFunc() {
    return engage_type
}

var event = {
    y: [engage_type[3].persona, engage_type[4].persona, engage_type[2].persona, engage_type[0].persona, engage_type[1].persona],
    x: [engage_type[3].Event, engage_type[4].Event, engage_type[2].Event, engage_type[0].Event, engage_type[1].Event],
    name: 'Event',
    type: 'bar',
    orientation: 'h',
    marker: {
      color: 'rgba(34, 58, 111,.9)',
      line: {
        color: 'rgb(34, 58, 111)',
        width: 2
      }
    }
  };
  
  var publication = {
    y: [engage_type[3].persona, engage_type[4].persona, engage_type[2].persona, engage_type[0].persona, engage_type[1].persona],
    x: [engage_type[3].Publication, engage_type[4].Publication, engage_type[2].Publication, engage_type[0].Publication, engage_type[1].Publication],
    name: 'Publication',
    type: 'bar',
    orientation: 'h',
    marker: {
      color: 'rgba(0,117,201,.8)',
      line: {
        color: 'rgb(0,74,152)',
        width: 2
      }
    }
  };
  
  var wg = {
    y: [engage_type[3].persona, engage_type[4].persona, engage_type[2].persona, engage_type[0].persona, engage_type[1].persona],
    x: [engage_type[3].WorkingGroup, engage_type[4].WorkingGroup, engage_type[2].WorkingGroup, engage_type[0].WorkingGroup, engage_type[1].WorkingGroup],
    name: 'Working Group',
    type: 'bar',
    orientation: 'h',
    marker: {
      color: 'rgba(230,75,5,.8)',
      line: {
        color: 'rgb(230,75,5)',
        width: 2
      }
    }
  };
  
  var data3 = [event, publication, wg];
  
  var layout = {
    title: "Total Engagements by Type",
    xaxis: { title: "Percent"},
    barmode: 'stack',
    yaxis: {
      showticklabels: false
    }
  };
  
  Plotly.newPlot('plot3', data3, layout);


//val() function executed on select and load
//Gets dropdown value, determines index of that value (sel), and renders plots/tables
function val() {  

    d = document.getElementById("Persona").value;
    //Get index of persona
    sel = 0

    if (d == 'Claire') {
    sel = 0;
    } else if (d == 'Dan') {
    sel = 1;
    } else if (d == 'Lynn') {
    sel = 2;
    } else if (d == 'Maya') {
    sel = 3;
    } else {
    sel = 4;
    };

    //Population growth
    function myFunc() {
        return pop_growth
    };

    console.log(pop_growth);

    var data4 = [{
    x: pop_growth[sel].x,
    y: pop_growth[sel].y,
    name: pop_growth[sel].persona,
    line: {color: '#223a6f'}
    }];

    var layout = {
    title: 'New Contacts Per Quarter',
    };


    Plotly.newPlot('plot4', data4, layout);

    //Engagement status

    function myFunc() {
        return recfreq
    };

    var data = [{
    values: [recfreq[sel].Active,recfreq[sel].New,recfreq[sel].Lapsed,recfreq[sel].Lost],
    labels: ['Active', 'New', 'Lapsed','Lost'],
    type: 'pie',
    marker: {
        colors: [
        '#223a6f',
        '#00a0df',
        '#d0d0ce',
        '#e64b38'
        ]
    }
    }];
    
    var layout = {
    title: 'Engagement Status'
    };
    
    Plotly.newPlot('plot5', data, layout);

    //Top items table

    function myFunc() {
        return top_items
    };

    //filter top_items by persona (d)
    filtered_items = top_items.filter( i => d.includes( i.persona ) );

    // Target the Table you want to insert the Data to
    // var results=document.getElementById('Items');

    var tableRef = document.getElementById('Items').getElementsByTagName('tbody')[0];

    for(var i = document.getElementById("Items").getElementsByTagName('tbody')[0].rows.length; i > 0;i--)
    {
        document.getElementById("Items").getElementsByTagName('tbody')[0].deleteRow(i -1);
    }

    for(var obj in filtered_items){
        // Insert a row in the table at row index 0
        var newRow   = tableRef.insertRow(tableRef.rows.length);

        // Insert a cell in the row at index 0
        var newCell  = newRow.insertCell(0);

        // Append a text node to the cell
        var newText  = document.createTextNode(filtered_items[obj].engagement)
        newCell.appendChild(newText);

        var newCell  = newRow.insertCell(1);

        var newText  = document.createTextNode(filtered_items[obj].count)
        newCell.appendChild(newText);
    };

    //Top campaigns table

    function myFunc() {
        return top_campaigns
    };
    
    //filter top_items by persona (d)
    filtered_campaigns = top_campaigns.filter( i => d.includes( i.persona ) );

    var tableRef = document.getElementById('Campaigns').getElementsByTagName('tbody')[0];

    for(var i = document.getElementById("Campaigns").getElementsByTagName('tbody')[0].rows.length; i > 0;i--)
    {
        document.getElementById("Campaigns").getElementsByTagName('tbody')[0].deleteRow(i -1);
    }

    for(var obj in filtered_campaigns){
        // Insert a row in the table at row index 0
        var newRow   = tableRef.insertRow(tableRef.rows.length);

        var newCell  = newRow.insertCell(0);
        var newText  = document.createTextNode(filtered_campaigns[obj].campaign)
        newCell.appendChild(newText);

        var newCell  = newRow.insertCell(1);
        var newText  = document.createTextNode(filtered_campaigns[obj].count)
        newCell.appendChild(newText);
    };
}; 

var select = document.getElementById("Persona");
select.onchange = val;
window.onload = val;
