### Included in home

<div class="card">
    <div class="card-body">
        <h5 class="card-title">List tickers of past dataset</h5>
        <p class="card-text">Please choose</p>
        <div class="input-group mb-3">
                <div class="input-group-prepend">
                    <label class="input-group-text" for="listable">Options</label>
                </div>
                <select class="custom-select form-control" id="listable">
                    <option selected>Choose...</option>
                    <%
                        import os
                        files = [f.replace('.json', '') for f in os.listdir('lists') if os.path.splitext(f)[1] == '.json']
                    %>
                    % for a in files:
                        <option value="${a}">${a}</option>
                    % endfor
                </select>
                <div class="input-group-append">
                    <button class="btn btn-primary" id="getTickers">List</button>
                </div>
            </div>
        <hr/>
        <div id="tickerList"></div>
    </div>
</div>