    $(document).ready(function () {
        $('#mapToggle button').click(function() {
            $(this).addClass('active').siblings().removeClass('active');
            if($(this).attr('id')=='map1'){
                quantize = d3.scale.quantile().domain([-4.5,-1]).range(d3.range(9));
                mapSettingRelative = true;
            }else{
                quantize = d3.scale.quantile().domain([0,3.2]).range(d3.range(9));
                mapSettingRelative = false;
            }
            updateMap();
        });

        function getArticles(articleIDs){
            var list = "<table class='table table-condensed table-hover' id='articleTable'><thead><tr><th class='col-date'>Datum</th><th class='col-link'>Titel</th></tr></thead><tbody>"
            articleIDs.forEach(function(id){
                list +="<tr><td class='col-date'>"+articles[id].date.split(" ")[0]+"</td><td class='col-link'><a href='http://www.nu.nl"+articles[id].link+"' target='_blank'>"+articles[id].title+"</a></td></tr>"
            });
            list += "</tbody></table>"
            return new Handlebars.SafeString(list);

        }

        var mapSettingRelative = true;
        var articles;

        $.getJSON("articlesData.json", function(json) {
            articles = json;
        });

       
        var dataTable = $("div#dataTableContainer");
        var tooltip = $("div#tooltipContainer");

        var source = $("#dataTable").html();
        var template = Handlebars.compile(source);
        var properties = {articleCount:"Geen plaats geselecteerd",
                          GM_NAAM:"Geen plaats geselecteerd",
                          population:"Geen plaats geselecteerd",
                          relativeArticleCount:"Geen plaats geselecteerd"};

        var html = template({d:properties, artikelen:"Geen plaats geselecteerd"});
        dataTable.html(html).show();

        var log = d3.scale.log();
        var quantize = d3.scale.quantile().domain([-4.5,-1.4]).range(d3.range(9));


        var xym = d3.geo.mercator();
        var path = d3.geo.path().projection(xym);

        // the variable that holds our translate, centers on the netherlands
        var translate = xym.translate();
        translate[0] = -550;
        translate[1] = 10620;

        // center on the netherlands and zoom all the way in
        xym.translate(translate);
        xym.scale(60000);

        var svg = d3.select("#chart")
                .append("svg")
                .attr("id", "svgoriginal")

        var gemeenten = svg.append("g");

        d3.json("data.json", function (json) {

            var selected;
            var tableCreated = false;
            gemeenten.selectAll("path")// select all the current path nodes
                    .data(json.features)// bind these to the features array in json
                    .enter().append("path")
                    .attr("d", path)
                    .attr('class', function (d) {
                        if(mapSettingRelative){
                            return "q" + quantize(log(d.properties.relativeArticleCount));
                        }else{
                            return "q" + quantize(log(d.properties.articleCount));
                        }
                    })
                    .on('click', function (d) {
                        if (selected){
                            selected.style('opacity', '')
                        }
                        d3.select(this).style('opacity', 1);
                        selected = d3.select(this)
                        var source = $("#dataTable").html();
                        var template = Handlebars.compile(source);
                        var html = template({d:d.properties, artikelen:getArticles(d.properties.articles)});
                        dataTable.html(html).show();
                        tableCreated = true;
                    })
                    .on('mouseover', function(d){
                        d3.select(this).style('opacity',1);
                        var source = $("#HBTooltip").html();
                        var template = Handlebars.compile(source);
                        var html = template({d:d.properties});
                        tooltip.html(html).show();
                    })
                    .on('mouseout', function(d){
                        if(tableCreated){
                            tableCreated = false;
                            $("#articleTable").addClass('Test');
                            var newTableObject = document.getElementById("articleTable")
                            sorttable.makeSortable(newTableObject);
                            var myTH = document.getElementsByTagName("th")[0];
                            sorttable.innerSortFunction.apply(myTH, []);
                        }
                        d3.select(this).style('opacity','');
                        tooltip.hide();
                    })
                    .on("mousemove", function () {
                        tooltip
                                .css("top", (event.pageY - 10) + "px")
                                .css("left", (event.pageX + 10) + "px");
                    });
            ;
        });

        function updateMap(){
            d3.json("data.json", function (json) {

                var selected;
                var tableCreated = false;
                gemeenten.selectAll("path")// select all the current path nodes
                        .attr('class', function (d) {
                            if(mapSettingRelative){
                                return "q" + quantize(log(d.properties.relativeArticleCount));
                            }else{
                                return "q" + quantize(log(d.properties.articleCount));
                            }
                        })
                        .on('click', function (d) {
                            if (selected){
                                selected.style('opacity', '')
                            }
                            d3.select(this).style('opacity', 1);
                            selected = d3.select(this)
                            var source = $("#dataTable").html();
                            var template = Handlebars.compile(source);
                            var html = template({d:d.properties, artikelen:getArticles(d.properties.articles)});
                            dataTable.html(html).show();
                            tableCreated = true;
                        })
                        .on('mouseover', function(d){
                            d3.select(this).style('opacity',1);
                            var source = $("#HBTooltip").html();
                            var template = Handlebars.compile(source);
                            var html = template({d:d.properties});
                            tooltip.html(html).show();
                        })
                        .on('mouseout', function(d){
                            if(tableCreated){
                                tableCreated = false;
                                $("#articleTable").addClass('Test');
                                var newTableObject = document.getElementById("articleTable")
                                sorttable.makeSortable(newTableObject);
                                var myTH = document.getElementsByTagName("th")[0];
                                sorttable.innerSortFunction.apply(myTH, []);
                            }
                            d3.select(this).style('opacity','');
                            tooltip.hide();
                        })
                        .on("mousemove", function () {
                            tooltip
                                    .css("top", (event.pageY - 10) + "px")
                                    .css("left", (event.pageX + 10) + "px");
                        });
                ;
            });
        }
    });