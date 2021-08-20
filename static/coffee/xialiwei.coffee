root = exports ? this
# !!!! Hotpoor xialiwei root object
root.Hs or= {}
Hs = root.Hs

$ ->
    console.log "Hello, I am xialiwei."

    handleFileSelect = (evt)->
        target_add_folder_file = $(".target_add_folder_file")
        target_add_folder_name = $(".target_add_folder_name").val()
        target_add_folder_dir = $(".target_add_folder_dir").val()

        formData = new FormData();

        formData.append("file",target_add_folder_file[0].files[0]);
        formData.append("folder_name", target_add_folder_name);
        formData.append("dir_name", target_add_folder_dir);

        url = "/*upload_file"
        $.ajax
            url:url
            data:formData
            dataType: 'json'
            type: 'POST'
            async: false
            processData : false # 使数据不做处理
            contentType : false # 不要设置Content-Type请求头
            success: (data) ->
                console.log data
                load_folder(target_add_folder_name,null)
                $(".target_add_folder_file")[0].outerHTML = $(".target_add_folder_file")[0].outerHTML
            error: (data) ->
                console.log data
    $("body").on "change", ".target_add_folder_file", handleFileSelect
    $("body").on "click",".add_folder_file",(evt)->
        $(".target_add_folder_file").click()

    $("body").on "click",".add_folder",(evt)->
        folder_name = $(".add_folder_name").val()
        add_folder(folder_name)
    $("body").on "click",".add_folder_new",(evt)->
        add_folder()
    $("body").on "input propertychange",".add_folder_name",(evt)->
        folder_name = $(".add_folder_name").val()
        search_folder_local(folder_name)
    root.search_folder_local = (folder_name="")->
        if folder_name == ""
            $(".card_folder_list_item").removeClass("hide")
        items = $(".card_folder_list_item")
        for item in items
            if $(item).text().indexOf(folder_name)==-1
                $(item).addClass("hide")
            else
                $(item).removeClass("hide")
    root.add_folder = (folder_name="")->
        if folder_name == ""
            folder_name = "新建文件夹"
        url = "/*add_folder"
        $.ajax
            url:url
            data:
                folder_name:folder_name
            dataType: 'json'
            type: 'POST'
            success: (data) ->
                console.log data
                load_folder_list()
            error: (data) ->
                console.log data
    $("body").on "click",".card_folder_list_item",(evt)->
        old_folder_name = $(".current_folder_name").text
        k = $(this).attr("data-k")
        v = $(this).attr("data-v")
        $(".current_folder_name").text k
        $(".add_folder_file").removeClass("hide")

        $(".target_add_folder_file")[0].outerHTML = $(".target_add_folder_file")[0].outerHTML
        $(".target_add_folder_name").val(k)
        $(".target_add_folder_dir").val("/")
        new_folder_name = k
        if old_folder_name != new_folder_name
            $(".card_content_list").empty()
        load_folder(k,v)
    load_folder = (folder_name=null,folder_meta_hash=null)->
        if folder_name == null or folder_name == ""
            return
        url = "/*get_folder"
        $.ajax
            url:url
            data:
                folder_name:folder_name
                t:(new Date()).getTime()
            dataType: 'json'
            type: 'GET'
            success: (data) ->
                console.log data
                folder_meta_hash = data.meta_hash
                load_folder_meta(folder_name,folder_meta_hash)
            error: (data) ->
                console.log data
    load_folder_meta = (folder_name=null,folder_meta_hash=null)->
        # $(".card_content_list").empty()
        oldlist = $(".card_content_list").find(".card_content_list_item")
        oldpathlist = []
        for item in oldlist
            oldpathlist.push $(item).find(".card_content_list_item_img").attr("src")
        if folder_name == null or folder_meta_hash == null or folder_name == "" or folder_meta_hash == ""
            return
        url = "/*get_meta"
        $.ajax
            url:url
            data:
                folder_meta_hash:folder_meta_hash
                t:(new Date()).getTime()
            dataType: 'json'
            type: 'GET'
            success: (data) ->
                console.log data
                if data == "no storage config"
                    return
                if data.items?
                    newpathlist = []
                    
                    for k,v of data.items
                        k_list = k.split(".")
                        pre_html = ""
                        file_type = k_list[k_list.length-1]
                        if file_type.toLocaleLowerCase() in ["jpg","jpeg","gif","png","webp","bmp"]
                            pre_html = """
                            <img class="card_content_list_item_img" src="/#{folder_name}/#{k}">
                            """
                        else if file_type.toLocaleLowerCase() in ["mov","m4a","mp4"]
                            pre_html = """
                            <video class="card_content_list_item_img" controls src="/#{folder_name}/#{k}">
                            """
                        newpathlist.push "/#{folder_name}/#{k}"
                        if "/#{folder_name}/#{k}" not in oldpathlist
                            $(".card_content_list").append """
                            <div class="card_content_list_item">
                                #{pre_html}
                                <div class="card_content_list_item_tools">
                                    <a href="/#{folder_name}/#{k}">下载</a>
                                </div>
                            </div>
                            """
            error: (data) ->
                console.log data
    load_folder_list = ()->
        $(".card_folder_list").empty()
        url = "/*get_folders"
        $.ajax
            url:url
            data:null
            dataType: 'json'
            type: 'GET'
            success: (data) ->
                console.log data
                for k,v of data.folders
                    $(".card_folder_list").append """
                    <div class="card_folder_list_item" data-k="#{k}" data-v="#{v}">#{k}</div>
                    """
            error: (data) ->
                console.log data
    load_ready_run = ()->
        load_folder_list()

    $(window).on "load",(evt)->
        load_ready_run()