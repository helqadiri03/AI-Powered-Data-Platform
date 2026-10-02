with source as (
    select * from {{ source('raw_ecommerce', 'reviews') }}
),

renamed as (
    select
        REVIEW_ID::varchar                                   as review_id,
        ORDER_ID::varchar                                    as order_id,
        try_to_number(REVIEW_SCORE::varchar)::int            as review_score,
        try_to_timestamp(REVIEW_CREATION_DATE::varchar)      as review_creation_date,
        try_to_timestamp(REVIEW_ANSWER_TIMESTAMP::varchar)   as review_answer_timestamp,
        REVIEW_COMMENT_TITLE::varchar                        as review_comment_title,
        REVIEW_COMMENT_MESSAGE::varchar                      as review_comment_message
    from source
    where try_to_number(REVIEW_SCORE::varchar) between 1 and 5
)

select * from renamed
