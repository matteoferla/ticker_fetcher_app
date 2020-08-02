<%inherit file="boilerplate.mako"/>

<div class="row text-center">
    <div class="col-12 col-md-4 offset-md-4">
    <form class="form-signin"  action="/login" method="post">
  <h1 class="h3 mb-3 font-weight-normal">Please authetiticate</h1>
  <label for="password" class="sr-only">Password</label>
  <input type="password" id="password" class="form-control" placeholder="Password" required>
  <div class="checkbox mb-3">
    <label>
      <input type="checkbox" value="remember-me" id="remember"> Remember me
    </label>
  </div>
  <button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>
</form>
    </div>
</div>