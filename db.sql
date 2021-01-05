create database trades;

use trades;

create table companies (
    name varchar(255) not null ,
    shortName varchar(10) not null ,
    active bit not null ,
    primary key (shortName)
);

create table openingPrices (
    date datetime not null ,
    open decimal(15,2) not null ,
    company varchar(10) not null ,
    primary key (date,company),
    foreign key (company) references companies(shortName)
);

create table predictions (
    "date" datetime not null ,
    company varchar(10) not null ,
    modelPredicted decimal(15,2) not null ,
    residual decimal(15,2),
    primary key (date,company),
    foreign key (company) references companies(shortName)
);

create trigger updateResidualTrigger after insert on openingPrices
    for each row
    begin
        declare modelPredictedTemp float;
        set modelPredictedTemp = (select modelPredicted from predictions where date=new.date);
        update predictions set residual=new.open-modelPredictedTemp where date=new.date;
    end;

create table predictionTableIndicator (
    indicator decimal(15,2),
    date datetime,
    rowNum integer primary key
);

create table actions (
    date datetime not null ,
    company varchar(10) not null ,
    boostedPrediction decimal(15,2) not null ,
    action enum('buy','sell') not null ,
    primary key (date,company),
    foreign key (company) references companies(shortName)
);

create trigger createAction after insert on predictions
    for each row
    begin
        declare boostedPred float;
        set boostedPred=NEW.modelPredicted-(select avg(residual) from predictions order by date desc limit 181);
        insert into actions (date, company, boostedPrediction, action)
        values (
            NEW.date,
            NEW.company,
            boostedPred,
            IF(boostedPred - (select open from openingPrices order by date desc limit 1) > 0, 'buy','sell')
            );
    end;

create table buyTrades (
    date datetime not null ,
    company varchar(10) not null ,
    numShares integer not null ,
    primary key (date,company),
    foreign key (company) references companies(shortName)
);

create table sellTrades (
    date datetime not null ,
    company varchar(10) not null ,
    numShares integer not null ,
    primary key (date,company),
    foreign key (company) references companies(shortName)
);

# create table sharesOwned (
#     date datetime not null ,
#     company varchar(10) not null ,
#     numShares integer not null ,
#     primary key (date,company),
#     foreign key (company) references companies(shortName)
# );

create view currentShares as
select buy.company, bought - sold as numShares from
(select company, sum(numShares) as sold from sellTrades group by company) as buy inner join


(select company, sum(numShares) as bought from buyTrades group by company) as sell on buy.company = sell.company;

# create view currentLiquidity as
# select 1000 - buyValue + sellValue from
# (select sum(numShares*buyPrice) as buyValue from buyTrades) as buy natural join
# (select sum(numShares*sellPrice) as sellValue from sellTrades) as sell;


select * from openingPrices order by date desc;
select * from predictions order by date desc ;
select * from actions order by date desc ;

insert into buyTrades ("date","company","numShares") values ('2021-01-05','FORD',10);

insert into buyTrades (date, company, numShares) value ('2021-01-05','FORD',10);



