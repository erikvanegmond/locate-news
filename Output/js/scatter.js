var margin = {top: 20, right: 80, bottom: 30, left: 50},
            w = 740 - margin.left - margin.right,
            h = 500 - margin.top - margin.bottom;

        var log = d3.scale.log();

        var xValue = function(d){return d.population;},
            xScale = d3.scale.linear(),
            xMap = function(d){return xScale(xValue(d));},
            xAxis = d3.svg.axis().scale(xScale).orient("bottom");

        var yValue = function(d){return d.articleCount;},
            yScale = d3.scale.linear(),
            yMap = function(d){return yScale(yValue(d));};
            yAxis = d3.svg.axis().scale(yScale).orient("left");
            

        var rValue = function(d){return log((d.articleCount+1)/d.population);},
            rScale = d3.scale.linear(),
            rMap = function(d){return rScale(rValue(d));};

        var dataName = function(d){return d.naam;}

        var zoom = d3.behavior.zoom();
                    
        var svg = d3.select("body")
                    .append("svg")
                    .attr("width", w + margin.left + margin.right)
                    .attr("height", h + margin.top + margin.bottom)
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");;

        var circle;

        var tooltip = d3.select("body").append("div")
                        .attr("class", "tooltip")
                        .style("opacity", 0);

        d3.json("locationData.json", function(data) {
            data.forEach(function(d) {
                d.population = +d.population;
                d.articleCount = +d.articleCount;
                d.naam = d.naam;
            });

            var xDomain = [-100000, d3.max(data, xValue)+0.05*d3.max(data, xValue)];
            xScale.domain(xDomain)
                  .range([0,w]);
            var yDomain = [-0.05*d3.max(data, yValue), d3.max(data, yValue)+0.05*d3.max(data, yValue)]
            yScale.domain(yDomain)
                  .range([h,0]);

            rScale.domain([d3.min(data, rValue), d3.max(data, rValue)])
                  .range([1,5]);
            
            zoom.x(xScale)
                .y(yScale)
                .scaleExtent([1,20])
                .on("zoom", zoomed);

            svg.call(zoom);

            svg.append("g")
               .attr("class", "x axis")  //Assign "axis" class
               .attr("transform", "translate(0," + h + ")")
               .call(xAxis)
               .append("text")
               .attr("class", "label")
               .attr("x", w)
               .attr("y", -6)
               .style("text-anchor", "end")
               .text("Aantal inwoners");

            svg.append("g")
               .attr("class", "y axis")
               .attr("transform", "translate(" + 63 + ",0)")
               .call(yAxis)
               .append("text")
               .attr("class", "label")
               .attr("transform", "rotate(-90)")
               .attr("y", 6)
               .attr("dy", "1em")
               .style("text-anchor", "end")
               .text("Aantal artikelen");

            circle = svg.selectAll("circle")
               .data(data)
               .enter()
               .append("circle")
               // .attr("cx", xMap)
               // .attr("cy", yMap)
               .attr("r", rMap)
               .attr("class", "dot")
               .attr("transform", transform)  
               .on("mouseover", function(d) {
                    tooltip.transition()
                        .style("opacity", 1);
                        tooltip.html(htmlTooltip(d))
                        .style("left", (d3.event.pageX + 20) + "px")
                        .style("top", (d3.event.pageY - 5) + "px");
                })
                .on("mouseout", function(d) {
                    tooltip.transition()
                        .style("opacity", 0)
                        tooltip.html("");
                });
            });

        function htmlTooltip(d){
            html = "<table class='table table-condensed'><tr><td colspan='2'>"+d.naam+"</td></tr><tr><td>Aantal artikelen</td><td>"+d.articleCount+"</td></tr><tr><td>Aantal inwoners</td><td>"+d.population+"</td></tr></table>"
            return html
        }

        function zoomed() {
            svg.select(".x.axis").call(xAxis);
            svg.select(".y.axis").call(yAxis); 
            circle.attr("transform", transform);
        }

        function transform(d) {
            return "translate(" + xMap(d) + "," + yMap(d) + ")";
        }