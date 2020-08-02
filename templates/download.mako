### Included in home

<div class="card">
            <div class="card-body">
                <h5 class="card-title">Download previous dataset</h5>
                <p class="card-text">These datasets are complete and ready for download.</p>
                <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <label class="input-group-text" for="downloadable">Options</label>
                        </div>
                        <select class="custom-select form-control" id="downloadable">
                            <option selected>Choose...</option>
                            <%
                                import os
                                files = [f for f in os.listdir('datasets') if os.path.splitext(f)[1] == '.csv']
                            %>
                            % for a in files:
                                <option value="${a}">${a}</option>
                            % endfor
                        </select>
                        <div class="input-group-append">
                            <button class="btn btn-primary" id="download">Download</button>
                        </div>
                    </div>
            </div>
        </div>