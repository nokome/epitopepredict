#!/usr/bin/env python

"""
    epitopepredict server app for viewing results, uses tornado
    Created Sep 2017
    Copyright (C) Damien Farrell
"""

import sys,os,glob
import pandas as pd
import numpy as np
from epitopepredict import base, web, analysis

import tornado.ioloop
import tornado.web
from wtforms_tornado import Form
from wtforms import TextField, StringField, FloatField, IntegerField, BooleanField
from wtforms import SelectField, SelectMultipleField
from wtforms import widgets
from tornado.web import RequestHandler
from bokeh.util.browser import view
from bokeh.plotting import figure
from bokeh.layouts import row, column, gridplot, widgetbox, layout
from bokeh.embed import components

wikipage = 'https://github.com/dmnfarrell/epitopepredict/wiki/Web-Application'
plotkinds = ['tracks','text','grid']
cut_methods = ['default','rank','score']
views = ['binders','promiscuous','by allele','summary']

def help_msg():
    msg = '<a>path for results not found, enter an existing folder with your results. </a> '
    msg += '<a href="%s"> see help page</a>' %wikipage
    return msg

def get_args(args):
    defaults = {'path':'','name':'','cutoff':5,'cutoff_method':'rank', 'pred':'tepitope',
                   'n':2,'kind':'tracks','view':'binders'}
    for k in defaults:
        if k in args:
            defaults[k] = args[k][0]
    return defaults

class ControlsForm(Form):
    name = SelectField('name', choices=[])
    path = TextField('path', default='results')
    cutoff = FloatField('cutoff', default=5)
    n = TextField('n', default='2')
    cm = [(i,i) for i in cut_methods]
    cutoff_method = SelectField('cutoff method', choices=cm)
    kinds = [(i,i) for i in plotkinds]
    kind = SelectField('plot kind', choices=kinds)
    views = [(i,i) for i in views]
    view = SelectField('view', choices=views)
    cached = BooleanField('use cached')

class SubmitForm(Form):
    path = TextField('path', default='results')
    pm = [(i,i) for i in base.predictors]
    predictors = SelectMultipleField('predictors', choices=pm)
    length = IntegerField('length', default=5)
    p1 = base.get_predictor('iedbmhc1')
    #x = [(i,i) for i in p1.getAlleles()]
    #mhc1alleles = SelectField('MHC-I alleles', choices=x)
    p2 = base.get_predictor('tepitope')
    x = [(i,i) for i in p2.getAlleles()]
    #drballeles = base.getDRBList(mhc2alleles)
    #dqpalleles = base.getDQPList(mhc2alleles)
    mhc2alleles = SelectMultipleField('MHC-II alleles', choices=x,
                                     option_widget=widgets.Select(multiple=True))
    mhc2alleles.size=5

class MainHandler(RequestHandler):
    """Handler for main results page"""
    def get(self):
        args = self.request.arguments
        buttons = ''
        self.render('index.html', buttons=buttons, path='')

class GlobalViewHandler(RequestHandler):
    """Handler for showing multiple sequences in a results folder"""

    def get(self):
        args = self.request.arguments
        form = ControlsForm()
        defaultargs = {'path':'','cutoff':5,'cutoff_method':'rank',
                       'view':'promiscuous','n':2,'cached':1}
        for k in defaultargs:
            if k in args:
                defaultargs[k] = args[k][0]
        path = defaultargs['path'].strip()
        view = defaultargs['view']
        usecached = defaultargs['cached']
        if usecached == 1:
            print ('using cached results')

        if not os.path.exists(path):
            msg = help_msg()
            self.render('global.html', form=form, msg=msg, path=path, status=0)

        preds = web.get_predictors(path)
        data = {}
        if view == 'summary':
            for P in preds:
                if P.data is None: continue
                seqs = web.get_sequences(P)
                #tables = web.sequences_to_html_table(seqs, classes="seqtable")
                pb = P.promiscuousBinders(**defaultargs)
                #print (pb)
                #cl = analysis.find_clusters(b, min_binders=2)
                x = pb.groupby('name').agg({'peptide':np.size,
                                            P.scorekey:np.median}).reset_index()
                x = x.rename(columns={'peptide':'binders'})
                x = x.merge(seqs, on='name', how='right')
                x = web.column_to_url(x, 'name', '/sequence?path=%s&name=' %path)
                data[P.name] = x
        else:
            data = web.get_binder_tables(preds, **defaultargs)
            #add url to prot/seq name
            for k in data:
                data[k] = web.column_to_url(data[k], 'name', '/sequence?path=%s&name=' %path)

        #convert dfs to html
        tables = web.dataframes_to_html(data, classes='tinytable sortable')
        #put tables in tabbed divs
        tables = web.tabbed_html(tables)

        form.path.data = path
        form.cutoff.data = defaultargs['cutoff']
        form.n.data = defaultargs['n']
        form.cutoff_method.data = defaultargs['cutoff_method']
        form.view.data = view

        self.render('global.html', form=form, tables=tables, msg='', status=1, path=path)

class GenomeViewHandler(RequestHandler):
    def get(self):
        args = self.request.arguments
        self.render('genome.html')

class SequenceViewHandler(RequestHandler):
    """Handler for main results page"""
    def get(self):

        args = self.request.arguments
        defaultargs = get_args(args)
        form = ControlsForm()
        path = defaultargs['path']
        current_name = defaultargs['name']

        if not os.path.exists(path):
            msg = help_msg()
            self.render('sequence.html', form=form, status=0, name='', msg=msg, path=path)
            return

        names = web.get_file_lists(path)
        if current_name == '': current_name = names[0]
        form.path.data = path
        form.name.choices = [(i,i) for i in names]
        form.name.data = current_name
        form.cutoff.data = defaultargs['cutoff']
        form.n.data = defaultargs['n']
        form.cutoff_method.data = defaultargs['cutoff_method']
        form.kind.data = defaultargs['kind']
        form.view.data = defaultargs['view']

        preds = web.get_predictors(path, current_name)
        #alleles = web.get_alleles(preds)

        data = web.get_binder_tables(preds, **defaultargs)
        tables = web.dataframes_to_html(data, classes='tinytable sortable')
        tables = web.tabbed_html(tables)
        #info = web.dict_to_html(web.get_results_info(preds[0]))
        info=''
        kind = defaultargs['kind']

        if kind == 'grid':
            seqhtml = web.sequence_to_html_grid(preds, classes="gridtable")
            div = '<div class="scrolled">%s</div>' %seqhtml
            script = ''
        elif kind == 'text':
            seqhtml = web.create_sequence_html(preds, classes="seqtable")
            div = '<div class="scrolled">%s</div>' %seqhtml
            script = ''
        else:
            plots = web.create_figures(preds, **defaultargs)

            if len(plots) > 0:
                grid = gridplot(plots, ncols=1, merge_tools=True, sizing_mode='scale_width',
                                toolbar_options=dict(logo=None))
                script, div = components(grid)
            else:
                script = ''; div = ''

        links = []
        for k in data.keys():
            defaultargs['pred'] = k
            links.append(self.get_url(defaultargs, link=k))

        self.render('sequence.html', script=script, div=div, form=form, tables=tables,
                    msg='', info=info, name=current_name, status=1, links=links, path=path)

    def get_url(self, args, link='download'):
        """Get url from current args"""

        import urllib
        s = '<a href=/download?'
        s += urllib.urlencode(args)
        s += '>%s<a>' %link
        return s

class DownloadHandler(RequestHandler):
    def get(self):
        args = self.request.arguments
        args = get_args(args)
        #args['method'] = 'tepitope'
        filename = args['name']+'_'+args['pred']+'.csv'
        self.set_header ('Content-Type', 'text/csv')
        self.set_header ('Content-Disposition', 'attachment; filename=%s' %filename)
        preds = web.get_predictors(args['path'], args['name'])
        data = web.get_binder_tables(preds, **args)
        out = self.get_csv(data, args['pred'])
        self.write (out)

    def get_csv(self, data, key):
        import io
        if key not in data: return ''
        df=data[key]
        output = io.BytesIO()
        df.to_csv(output, float_format='%.2f')
        csvdata = output.getvalue()
        return csvdata

class SubmitJobHandler(RequestHandler):
    def get(self):
        args = self.request.arguments
        defaultargs = get_args(args)
        form = SubmitForm()
        path = defaultargs['path']
        #current_name = defaultargs['name']
        helptext = 'The usual method is to select one or more predictors and appropriate alleles '\
                   'which are then run at once for all the proteins in the chosen genome. '\
                   'An entire proteome using multiple methods may take several hours to process. '
        self.render('submit.html', form=form, path=path, helptext=helptext)

settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        autoescape=None,
        xsrf_cookies=True,
        debug=True)

def main(port=8888):
    #bokeh_app = Application(FunctionHandler(IndexHandler.modify_doc))
    #bokeh_server = Server({'/main': bokeh_app},
    #                      io_loop=io_loop,
    #                      extra_patterns=[('/', IndexHandler)],
    #                      allow_websocket_origin=['localhost:5006'])
    #bokeh_server.start()
    handlers = [ (r"/", MainHandler),
                 (r"/sequence", SequenceViewHandler),
                 (r"/global", GlobalViewHandler),
                 (r"/submit", SubmitJobHandler),
                 (r"/download", DownloadHandler)
                 ]
    app = tornado.web.Application(handlers, **settings)
    #app.listen(8888)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    io_loop = tornado.ioloop.IOLoop.current()
    #io_loop.add_callback(view, "http://localhost:8888/")
    view("http://localhost:8888/")
    io_loop.start()


if __name__ == "__main__":
    main()