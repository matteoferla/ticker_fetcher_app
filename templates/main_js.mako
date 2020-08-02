<%
    import os
%>
<script type="text/javascript">
    window.financial = '${os.environ['FINANCIAL_KEY']}';
        <%text>
            $(document).ready(() => {
                //tickers
                $('#getTickers').click(event => {
                    $.get('get_tickers', {
                        dataset: listable.value,
                        key: window.financial
                    })
                            .then(msg => {
                                tickerList.innerHMTL = msg;
                            });
                });
                // download
                $('#download').click(event => {
                    $.get('download', {
                        dataset: downloadable.value,
                        key: window.financial
                    })
                            .then(msg => {
                                let element = document.createElement('a');
                                element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(msg));
                                element.setAttribute('download', downloadable.value);
                                element.style.display = 'none';
                                document.body.appendChild(element);
                                element.click();
                                document.body.removeChild(element);
                            });
                });
                // retrieve
                $('#retrieve').click(event => {
                    $.get('retrieve', {
                        name: datasetName.value,
                        tickers: tickers.value,
                        key: window.financial
                    })
                            .then(msg => alert('Dataset will be downloaded and you will be notified.'));
                });
            });
        </%text>
</script>