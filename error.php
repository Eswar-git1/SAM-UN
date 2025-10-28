Failed to refresh SITREPs: Error: <!doctype html>
<html lang=en>
  <head>
    <title>KeyError: &#39;lon&#39;
 // Werkzeug Debugger</title>
    <link rel="stylesheet" href="?__debugger__=yes&amp;cmd=resource&amp;f=style.css">
    <link rel="shortcut icon"
        href="?__debugger__=yes&amp;cmd=resource&amp;f=console.png">
    <script src="?__debugger__=yes&amp;cmd=resource&amp;f=debugger.js"></script>
    <script>
      var CONSOLE_MODE = false,
          EVALEX = true,
          EVALEX_TRUSTED = false,
          SECRET = "fQB7XRtgUEim46sxQMls";
    </script>
  </head>
  <body style="background-color: #fff">
    <div class="debugger">
<h1>KeyError</h1>
<div class="detail">
  <p class="errormsg">KeyError: &#39;lon&#39;
</p>
</div>
<h2 class="traceback">Traceback <em>(most recent call last)</em></h2>
<div class="traceback">
  <h3></h3>
  <ul><li><div class="frame" id="frame-2653520388752">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">1536</em>,
      in <code class="function">__call__</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">    </span>) -&gt; cabc.Iterable[bytes]:</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;The WSGI server calls the Flask application object as the</pre>
<pre class="line before"><span class="ws">        </span>WSGI application. This calls :meth:`wsgi_app`, which can be</pre>
<pre class="line before"><span class="ws">        </span>wrapped to apply middleware.</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;</pre>
<pre class="line current"><span class="ws">        </span>return self.wsgi_app(environ, start_response)
<span class="ws">        </span>       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre></div>
</div>

<li><div class="frame" id="frame-2653520389904">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_socketio\__init__.py"</cite>,
      line <em class="line">42</em>,
      in <code class="function">__call__</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">                         </span>socketio_path=socketio_path)</pre>
<pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">    </span>def __call__(self, environ, start_response):</pre>
<pre class="line before"><span class="ws">        </span>environ = environ.copy()</pre>
<pre class="line before"><span class="ws">        </span>environ[&#39;flask.app&#39;] = self.flask_app</pre>
<pre class="line current"><span class="ws">        </span>return super().__call__(environ, start_response)
<span class="ws">        </span>       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws"></span>class _ManagedSession(dict, SessionMixin):</pre>
<pre class="line after"><span class="ws">    </span>&#34;&#34;&#34;This class is used for user sessions that are managed by</pre>
<pre class="line after"><span class="ws">    </span>Flask-SocketIO. It is simple dict, expanded with the Flask session</pre></div>
</div>

<li><div class="frame" id="frame-2653520390336">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\engineio\middleware.py"</cite>,
      line <em class="line">74</em>,
      in <code class="function">__call__</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">                    </span>&#39;200 OK&#39;,</pre>
<pre class="line before"><span class="ws">                    </span>[(&#39;Content-Type&#39;, static_file[&#39;content_type&#39;])])</pre>
<pre class="line before"><span class="ws">                </span>with open(static_file[&#39;filename&#39;], &#39;rb&#39;) as f:</pre>
<pre class="line before"><span class="ws">                    </span>return [f.read()]</pre>
<pre class="line before"><span class="ws">            </span>elif self.wsgi_app is not None:</pre>
<pre class="line current"><span class="ws">                </span>return self.wsgi_app(environ, start_response)
<span class="ws">                </span>       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">        </span>return self.not_found(start_response)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def not_found(self, start_response):</pre>
<pre class="line after"><span class="ws">        </span>start_response(&#34;404 Not Found&#34;, [(&#39;Content-Type&#39;, &#39;text/plain&#39;)])</pre>
<pre class="line after"><span class="ws">        </span>return [b&#39;Not Found&#39;]</pre></div>
</div>

<li><div class="frame" id="frame-2653520389472">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">1514</em>,
      in <code class="function">wsgi_app</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">            </span>try:</pre>
<pre class="line before"><span class="ws">                </span>ctx.push()</pre>
<pre class="line before"><span class="ws">                </span>response = self.full_dispatch_request()</pre>
<pre class="line before"><span class="ws">            </span>except Exception as e:</pre>
<pre class="line before"><span class="ws">                </span>error = e</pre>
<pre class="line current"><span class="ws">                </span>response = self.handle_exception(e)
<span class="ws">                </span>           ^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">            </span>except:  # noqa: B001</pre>
<pre class="line after"><span class="ws">                </span>error = sys.exc_info()[1]</pre>
<pre class="line after"><span class="ws">                </span>raise</pre>
<pre class="line after"><span class="ws">            </span>return response(environ, start_response)</pre>
<pre class="line after"><span class="ws">        </span>finally:</pre></div>
</div>

<li><div class="frame" id="frame-2653520390048">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py"</cite>,
      line <em class="line">176</em>,
      in <code class="function">wrapped_function</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">        </span># These error handlers will still respect the behavior of the route</pre>
<pre class="line before"><span class="ws">        </span>if options.get(&#34;intercept_exceptions&#34;, True):</pre>
<pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">            </span>def _after_request_decorator(f):</pre>
<pre class="line before"><span class="ws">                </span>def wrapped_function(*args, **kwargs):</pre>
<pre class="line current"><span class="ws">                    </span>return cors_after_request(app.make_response(f(*args, **kwargs)))
<span class="ws">                    </span>                                            ^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">                </span>return wrapped_function</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">            </span>if hasattr(app, &#34;handle_exception&#34;):</pre>
<pre class="line after"><span class="ws">                </span>app.handle_exception = _after_request_decorator(app.handle_exception)</pre></div>
</div>

<li><div class="frame" id="frame-2653520389328">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">1511</em>,
      in <code class="function">wsgi_app</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">        </span>ctx = self.request_context(environ)</pre>
<pre class="line before"><span class="ws">        </span>error: BaseException | None = None</pre>
<pre class="line before"><span class="ws">        </span>try:</pre>
<pre class="line before"><span class="ws">            </span>try:</pre>
<pre class="line before"><span class="ws">                </span>ctx.push()</pre>
<pre class="line current"><span class="ws">                </span>response = self.full_dispatch_request()
<span class="ws">                </span>           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">            </span>except Exception as e:</pre>
<pre class="line after"><span class="ws">                </span>error = e</pre>
<pre class="line after"><span class="ws">                </span>response = self.handle_exception(e)</pre>
<pre class="line after"><span class="ws">            </span>except:  # noqa: B001</pre>
<pre class="line after"><span class="ws">                </span>error = sys.exc_info()[1]</pre></div>
</div>

<li><div class="frame" id="frame-2653520390624">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">919</em>,
      in <code class="function">full_dispatch_request</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">            </span>request_started.send(self, _async_wrapper=self.ensure_sync)</pre>
<pre class="line before"><span class="ws">            </span>rv = self.preprocess_request()</pre>
<pre class="line before"><span class="ws">            </span>if rv is None:</pre>
<pre class="line before"><span class="ws">                </span>rv = self.dispatch_request()</pre>
<pre class="line before"><span class="ws">        </span>except Exception as e:</pre>
<pre class="line current"><span class="ws">            </span>rv = self.handle_user_exception(e)
<span class="ws">            </span>     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">        </span>return self.finalize_request(rv)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def finalize_request(</pre>
<pre class="line after"><span class="ws">        </span>self,</pre>
<pre class="line after"><span class="ws">        </span>rv: ft.ResponseReturnValue | HTTPException,</pre></div>
</div>

<li><div class="frame" id="frame-2653520390192">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py"</cite>,
      line <em class="line">176</em>,
      in <code class="function">wrapped_function</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">        </span># These error handlers will still respect the behavior of the route</pre>
<pre class="line before"><span class="ws">        </span>if options.get(&#34;intercept_exceptions&#34;, True):</pre>
<pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">            </span>def _after_request_decorator(f):</pre>
<pre class="line before"><span class="ws">                </span>def wrapped_function(*args, **kwargs):</pre>
<pre class="line current"><span class="ws">                    </span>return cors_after_request(app.make_response(f(*args, **kwargs)))
<span class="ws">                    </span>                                            ^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">                </span>return wrapped_function</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">            </span>if hasattr(app, &#34;handle_exception&#34;):</pre>
<pre class="line after"><span class="ws">                </span>app.handle_exception = _after_request_decorator(app.handle_exception)</pre></div>
</div>

<li><div class="frame" id="frame-2653520390480">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">917</em>,
      in <code class="function">full_dispatch_request</code></h4>
  <div class="source library"><pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">        </span>try:</pre>
<pre class="line before"><span class="ws">            </span>request_started.send(self, _async_wrapper=self.ensure_sync)</pre>
<pre class="line before"><span class="ws">            </span>rv = self.preprocess_request()</pre>
<pre class="line before"><span class="ws">            </span>if rv is None:</pre>
<pre class="line current"><span class="ws">                </span>rv = self.dispatch_request()
<span class="ws">                </span>     ^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">        </span>except Exception as e:</pre>
<pre class="line after"><span class="ws">            </span>rv = self.handle_user_exception(e)</pre>
<pre class="line after"><span class="ws">        </span>return self.finalize_request(rv)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def finalize_request(</pre></div>
</div>

<li><div class="frame" id="frame-2653520390768">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py"</cite>,
      line <em class="line">902</em>,
      in <code class="function">dispatch_request</code></h4>
  <div class="source library"><pre class="line before"><span class="ws">            </span>and req.method == &#34;OPTIONS&#34;</pre>
<pre class="line before"><span class="ws">        </span>):</pre>
<pre class="line before"><span class="ws">            </span>return self.make_default_options_response()</pre>
<pre class="line before"><span class="ws">        </span># otherwise dispatch to the handler for that endpoint</pre>
<pre class="line before"><span class="ws">        </span>view_args: dict[str, t.Any] = req.view_args  # type: ignore[assignment]</pre>
<pre class="line current"><span class="ws">        </span>return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
<span class="ws">        </span>       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def full_dispatch_request(self) -&gt; Response:</pre>
<pre class="line after"><span class="ws">        </span>&#34;&#34;&#34;Dispatches the request and on top of that performs request</pre>
<pre class="line after"><span class="ws">        </span>pre and postprocessing as well as HTTP exception catching and</pre>
<pre class="line after"><span class="ws">        </span>error handling.</pre></div>
</div>

<li><div class="frame" id="frame-2653520390912">
  <h4>File <cite class="filename">"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\app.py"</cite>,
      line <em class="line">238</em>,
      in <code class="function">api_sitreps_geojson</code></h4>
  <div class="source "><pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">        </span>feature = {</pre>
<pre class="line before"><span class="ws">            </span>&#34;type&#34;: &#34;Feature&#34;,</pre>
<pre class="line before"><span class="ws">            </span>&#34;geometry&#34;: {</pre>
<pre class="line before"><span class="ws">                </span>&#34;type&#34;: &#34;Point&#34;,</pre>
<pre class="line current"><span class="ws">                </span>&#34;coordinates&#34;: [sitrep[&#39;lon&#39;], sitrep[&#39;lat&#39;]]
<span class="ws">                </span>                ^^^^^^^^^^^^^</pre>
<pre class="line after"><span class="ws">            </span>},</pre>
<pre class="line after"><span class="ws">            </span>&#34;properties&#34;: {</pre>
<pre class="line after"><span class="ws">                </span>&#34;id&#34;: sitrep[&#39;id&#39;],</pre>
<pre class="line after"><span class="ws">                </span>&#34;source&#34;: sitrep[&#39;source&#39;],</pre>
<pre class="line after"><span class="ws">                </span>&#34;source_category&#34;: sitrep.get(&#39;source_category&#39;, &#39;&#39;),</pre></div>
</div>
</ul>
  <blockquote>KeyError: &#39;lon&#39;
</blockquote>
</div>

<div class="plain">
    <p>
      This is the Copy/Paste friendly version of the traceback.
    </p>
    <textarea cols="50" rows="10" name="code" readonly>Traceback (most recent call last):
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 1536, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_socketio\__init__.py&#34;, line 42, in __call__
    return super().__call__(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\engineio\middleware.py&#34;, line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 1514, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py&#34;, line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 1511, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 919, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py&#34;, line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 917, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py&#34;, line 902, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File &#34;C:\Users\Sarvam AI\Desktop\sam un\SAM UN\app.py&#34;, line 238, in api_sitreps_geojson
    &#34;coordinates&#34;: [sitrep[&#39;lon&#39;], sitrep[&#39;lat&#39;]]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: &#39;lon&#39;
</textarea>
</div>
<div class="explanation">
  The debugger caught an exception in your WSGI application.  You can now
  look at the traceback which led to the error.  <span class="nojavascript">
  If you enable JavaScript you can also use additional features such as code
  execution (if the evalex feature is enabled), automatic pasting of the
  exceptions and much more.</span>
</div>
      <div class="footer">
        Brought to you by <strong class="arthur">DON'T PANIC</strong>, your
        friendly Werkzeug powered traceback interpreter.
      </div>
    </div>

    <div class="pin-prompt">
      <div class="inner">
        <h3>Console Locked</h3>
        <p>
          The console is locked and needs to be unlocked by entering the PIN.
          You can find the PIN printed out on the standard output of your
          shell that runs the server.
        <form>
          <p>PIN:
            <input type=text name=pin size=14>
            <input type=submit name=btn value="Confirm Pin">
        </form>
      </div>
    </div>
  </body>
</html>

<!--

Traceback (most recent call last):
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 1536, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_socketio\__init__.py", line 42, in __call__
    return super().__call__(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\engineio\middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 1514, in wsgi_app
    response = self.handle_exception(e)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py", line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 1511, in wsgi_app
    response = self.full_dispatch_request()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 919, in full_dispatch_request
    rv = self.handle_user_exception(e)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask_cors\extension.py", line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 917, in full_dispatch_request
    rv = self.dispatch_request()
         ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\venv\Lib\site-packages\flask\app.py", line 902, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Sarvam AI\Desktop\sam un\SAM UN\app.py", line 238, in api_sitreps_geojson
    "coordinates": [sitrep['lon'], sitrep['lat']]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'lon'


-->

    at refreshSitreps (main.js:3230:24)
    at async main.js:555:9