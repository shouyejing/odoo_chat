# -*- coding: utf-8 -*-
import logging
import werkzeug
import json

from openerp import SUPERUSER_ID
from openerp import http
from datetime import datetime, timedelta
from openerp.http import request
import base64
from openerp.addons.website_blog.controllers.main import WebsiteBlog
from openerp.osv.orm import browse_record
from openerp.addons.website.models.website import slug, unslug

PPG = 20 # Products Per Page
PPR = 4  # Products Per Row

_logger = logging.getLogger(__name__)


class QueryURL(object):
    def __init__(self, path='', path_args=None, **args):
        self.path = path
        self.args = args
        self.path_args = set(path_args or [])

    def __call__(self, path=None, path_args=None, **kw):
        path = path or self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        path_args = set(path_args or []).union(self.path_args)
        paths, fragments = [], []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, browse_record):
                    paths.append((key, slug(value)))
                else:
                    paths.append((key, value))
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(werkzeug.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.url_encode([(key, value)]))
        for key, value in paths:
            path += '/' + key + '/%s' % value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class website_vote(http.Controller):
    # @http.route([
    #     '/vote-form',
    # ], type='http', auth="user", website=True)
    # def voteform(self):
    #     cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
    #     return request.website.render("website_vote.website_vote_form")

    @http.route([
        '/vote-submit/',
    ], type='http', auth="user", methods=['POST'], website=True)
    def vote_submit(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        date_from = '2017/01/24 08:30:00'
        date_to = '2017/02/18 23:59:59'
        date_now = (datetime.now() + timedelta(hours=7)).strftime("%Y/%m/%d %H:%M:%S")
        print date_from
        print date_to
        print date_now
        if date_from < date_now < date_to:
            print 'thoa man date'
            if kwargs.get('blog_post_id'):
                vote = pool.get('vote').search(cr, uid, [('user_id', '=', uid),
                                                         ('blog_post_id', '=', int(kwargs.get('blog_post_id')))])
                if not vote:
                    print 'thoa man vote'
                    vote_id = pool.get('vote').create(cr, uid, {'user_id': uid, 'blog_post_id': kwargs.get('blog_post_id')})
        if request.httprequest and request.httprequest.headers.environ.get('HTTP_REFERER'):
            url = request.httprequest.headers.environ.get('HTTP_REFERER')
        else:
            url = '/blog/'
        return request.redirect(url)

    @http.route([
        '/result/',
    ], type='http', auth="public", website=True)
    def result(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        cr.execute("""select count(*) as top, blog_post_id from vote group by blog_post_id order by top desc""")
        top_vote = cr.fetchall()
        values = []
        for vote in top_vote:
            if vote[0]:
                blog_post = pool.get('blog.post').browse(cr, uid, vote[1])
                data = {
                    'blog_post': blog_post,
                    'vote': vote[0],
                }
            values.append(data)
        list_blog = {
            'list_blog': values,
            'blog_url': QueryURL('', ['blog', 'tag'])
        }
        return request.website.render("website_vote.website_vote_result_form", list_blog)

    @http.route([
        '/top-vote/',
    ], type='http', auth="public", website=True)
    def top_vote(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        blog_post_ids = pool.get('blog.post').search(cr, uid, [])

        blog_post = pool.get('blog.post').browse(cr, uid, blog_post_ids)

        list_blog = {
            'list_blog': blog_post,
        }
        return request.website.render("website_vote.website_vote_form",
                                      list_blog)


    # @http.route([
    #     '/vote-form',
    # ], type='http', auth="user", website=True)
    # def voteform(self):
    #     cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
    #     return request.website.render("website_vote_list")


class website_blog_post(WebsiteBlog):
    @http.route([
        '''/blog/<model("blog.blog"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        cr, uid, context = request.cr, request.uid, request.context
        tag_obj = request.registry['blog.tag']
        blog_post_obj = request.registry['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blogpost/%s" % blog_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(blog_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = blog_post.website_message_ids[pager_begin:pager_end]

        tag = None
        if tag_id:
            tag = request.registry['blog.tag'].browse(request.cr, request.uid, int(tag_id), context=request.context)
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/post/%s" % (slug(blog_post.blog_id), slug(blog_post)))

        tags = tag_obj.browse(cr, uid, tag_obj.search(cr, uid, [], context=context), context=context)

        # Find next Post
        all_post_ids = blog_post_obj.search(cr, uid, [('blog_id', '=', blog.id)], context=context)
        # should always return at least the current post
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and blog_post_obj.browse(cr, uid, next_post_id, context=context) or False
        vote_count = request.registry['vote'].search_count(cr, uid, [('blog_post_id', '=', blog_post.id)])

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blog_post_cover_properties': json.loads(blog_post.cover_properties),
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'next_post_cover_properties': json.loads(next_post.cover_properties) if next_post else {},
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'comments': comments,
            'vote_count': vote_count,
        }
        response = request.website.render("website_blog.blog_post_complete", values)

        request.session[request.session_id] = request.session.get(request.session_id, [])
        if not (blog_post.id in request.session[request.session_id]):
            request.session[request.session_id].append(blog_post.id)
            # Increase counter
            blog_post_obj.write(cr, SUPERUSER_ID, [blog_post.id], {
                'visits': blog_post.visits + 1,
            }, context=context)
        return response



