<div class="card">
            <div class="card-body">
                <h5 class="card-title">Request new retrieval</h5>
                <p class="card-text">These datasets are complete and ready for download. Date with be added automatically to name.</p>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <label class="input-group-text" for="datasetName">dataset name</label>
                    </div>
                    <input type="text" class="form-control" placeholder="mydata" id="datasetName">
                </div>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <label class="input-group-text" for="tickers">Ticker list</label>
                    </div>
                    <textarea class="form-control" id="tickers" rows="10"></textarea>
                    <div class="input-group-append">
                        <button class="btn btn-primary" id="retrieve">Retrieve</button>
                    </div>
                </div>
            </div>
        </div>