const url_site = 'http://127.0.0.1:5002/';

function parse_the_data(json_data, search){//parsing data from the json to array of object
  //search à true si c'est une recherche
  if (search){
    create_tab(json_data);
  }
  else{
    list_college(json_data);
  }
}

function create_tab(json_data){
  let container = document.getElementsByClassName("col col-12 mx-auto")[0];

  let tab_tag = document.createElement("table");
  tab_tag.classList.add("table");

  let tabhead_tag = document.createElement("thead");

  let tr_1_tag = document.createElement("tr");

  let th_tag = document.createElement("th");
  th_tag.innerHTML = "Search result"

  let tbody_tag = document.createElement("tbody");
  json_data.data.forEach(function(element){
    tr_temp = document.createElement("tr");
    td_temp = document.createElement("td");
    td_temp.innerHTML = element;

    tr_temp.appendChild(td_temp)
    tbody_tag.appendChild(tr_temp);
  });
  tr_1_tag.appendChild(th_tag);
  tabhead_tag.appendChild(tr_1_tag);
  tab_tag.appendChild(tabhead_tag);
  tab_tag.appendChild(tbody_tag);
  container.appendChild(tab_tag);
}

function list_college(json_data){
  let container = document.getElementById("list_college");
  json_data.data.forEach(function(element){
    temp_option = document.createElement("option");
    temp_option.value = element.Code;
    temp_option.setAttribute("id",element.Code)
    temp_option.innerHTML = element.Nom
    container.appendChild(temp_option);
  });
}

function get_data(options){
  //getting data from the api
  fetch(url_site+'make_search?'+options)
    .then(response => response.json())
    .then(data => parse_the_data(data,true))
    .catch(err => console.error(err));
}

function getRequests() {
    var s1 = location.search.substring(1, location.search.length).split('&'),
        r = {}, s2, i;
    for (i = 0; i < s1.length; i += 1) {
        s2 = s1[i].split('=');
        r[decodeURIComponent(s2[0]).toLowerCase()] = decodeURIComponent(s2[1]);
    }
    return r;
};

function get_college(){
  fetch(url_site+'get_college')
    .then(response => response.json())
    .then(data => parse_the_data(data))
    .then(function() {form_parser()})
    .catch(err => console.error(err));
}

function selectItemByValue(elmnt, value){
  for(var i=0; i < elmnt.options.length; i++)
  {
    if(elmnt.options[i].value == value)
      elmnt.selectedIndex = i;
  }
}


function form_parser(){
  let QueryString = getRequests();
  if (QueryString["search_field"] !== undefined){
    document.getElementsByName("search_field")[0].value = QueryString['search_field'];
    selectItemByValue(document.getElementsByName('college_field')[0],QueryString['college_field']);
    document.getElementsByName('time_start_field')[0].value = QueryString['time_start_field'];
    document.getElementsByName("time_stop_field")[0].value = QueryString['time_stop_field'];
    document.getElementsByName("date_field")[0].value = QueryString['date_field'];
    get_data(window.location.search.substr(1));
  }
}

//fonction de parsing des options de la requête GET
function getRequests() {
    var s1 = location.search.substring(1, location.search.length).split('&'),
        r = {}, s2, i;
    for (i = 0; i < s1.length; i += 1) {
        s2 = s1[i].split('=');
        r[decodeURIComponent(s2[0]).toLowerCase()] = decodeURIComponent(s2[1]);
    }
    return r;
};

function parse_get_onload(){
  get_college();//we get the college value
}
