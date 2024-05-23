const manageTag = (() => {
   const getTags = async (keyword, page, callback) => {
       const response = await fetch(`/managers-page/tags/api/?keyword=${keyword}&page=${page}`)
       const tags = await response.json()

       if(callback){
           return callback(tags)
       }
       return tags
   }

   const remove = async (tagList) => {
       await fetch(`/managers-page/tags/api/`, {
           method: 'DELETE',
           headers: {
               'Content-Type': 'application/json;charset=utf-8',
               'X-CSRFToken': csrf_token
           },
           body: JSON.stringify(tagList)
       })
   }

    return {getTags: getTags, remove: remove}
})()