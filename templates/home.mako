<%inherit file="boilerplate.mako"/>

<div class="row">
    <div class="col-12 p-5">
            <%include file="download.mako"/>
    </div>
    <div class="col-12 p-5">
            <%include file="retrieve.mako"/>
    </div>
        <div class="col-12 p-5">
            <%include file="get_tickers.mako"/>
    </div>
</div>

<%block name="script">
    <%include file="main_js.mako"/>
</%block>

