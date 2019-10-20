const colors = {
            pink: '#f92672',
            green: '#a6e22e',
            blue: '#66d9ef',
            orange: '#fd971f',
            purple: '#ae81ff'
        }

        function combineData(data) {
        // Returns crossfilter of combined results.
            let combined = []
            Object.keys(data).forEach((type) => {
                data[type].forEach((record) => {
                    record.type = type;
                    record.date = d3.time.format('%Y-%m-%d').parse(record.date.slice(0, 10));
                });
                combined = combined.concat(data[type]);
            });

            return combined;
        }

        function createGroupFrom(dimension, type) {
            // Creates a grouping from the given engagement type.
            let group =  dimension.group().reduce(
                (p, v) => {
                    if (v.type === type) p.total += v.total;
                    return p;
                }, (p, v) => {
                    if (v.type === type) p.total -= v.total;
                    return p;
                }, () => {
                    return {total: 0, type: type};
            });
            
            // Create a fake group to show start and end of engagement spikes.
            let fakeGroup = {
                all() {
                    let newGroup = [];
                    group.all().forEach((record) => {
                        if (record.value.total > 0) {
                            let prevDay = new Date(record.key.getTime() - 86400000);
                            if (!newGroup.find(newRecord => newRecord.key.getTime() == prevDay.getTime())) {
                                newGroup.push({key: prevDay, value: {total: 0, type: type}});
                            }

                            newRecordIndex = newGroup.findIndex(newRecord => newRecord.key.getTime() == record.key.getTime());
                            if (newRecordIndex === -1) newGroup.push(record);
                            else newGroup[newRecordIndex].value.total += record.value.total;

                            let nextDay = new Date(record.key.getTime() + 86400000)
                            if (!newGroup.find(newRecord => newRecord.key.getTime() == nextDay.getTime())) {
                                newGroup.push({key: nextDay, value: {total: 0, type: type}});
                            }
                        }
                    });

                    return newGroup;
                }
            }

            return fakeGroup;
        }

        function createLineChart(chart, dimension, group, color=colors.blue, title=(d) => `${d.key.toDateString()}: ${d.value.total} ${d.value.type}`) {
            // Create a line chart for the group to use as part of the composite.
            return dc.lineChart(chart)
                     .dimension(dimension)
                     .group(group)
                     .valueAccessor((d) => d.value.total)
                     .title(title)
                     .colors(color)
                     .transitionDuration(500)
        }

        function createCompositeChart(chartID, ndx, groups) {
            // Create a composite line chart of named groups
            let chart = dc.compositeChart('#' + chartID);

            let dateDim = ndx.dimension(dc.pluck('date'));
            let minDate, maxDate;
            
            // If the date range has been set by the user, use that range for the chart, otherwise use defaults.
            if ($('#id_start_date').val() != '') minDate = d3.time.format('%Y-%m-%d').parse($('#id_start_date').val());
            else minDate = new Date(dateDim.bottom(1)[0].date - 86400000)
            if ($('#id_end_date').val() != '') maxDate = d3.time.format('%Y-%m-%d').parse($('#id_end_date').val());
            else maxDate = new Date().setHours(0,0,0,0);
            
            // Set up the chart.
            chart.margins({ top: 15, right: 50, left: 50, bottom: 30 })
                 .brushOn(false)
                 .transitionDuration(500)
                 .shareTitle(false)
                 .x(d3.time.scale().domain([minDate, maxDate]))
                 .yAxis().ticks(4);
            
            // Add line charts for each group.
            chart.compose(groups.map(group => createLineChart(chart, dateDim, createGroupFrom(dateDim, group.name), group.color, group.title)));

            return chart;
        }
