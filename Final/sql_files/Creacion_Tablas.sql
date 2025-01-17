create table Entidad (
id_Movimientos int primary key,

Fecha date,

Nombre_entidad varchar(100),

cod_negocio int,

cod_transaccion int ,

foreign key (Nombre_entidad) references identificacion(Nombre_entidad), 	
	
foreign key (cod_transaccion) references Rentabilidad(cod_transaccion),

foreign key (cod_negocio) references Negocio(cod_negocio)

);


create table Identificacion(

tipo_entidad int,

cod_entidad int,

Nombre_entidad varchar(100) primary key

);



create table Negocio(

cod_negocio int primary key,

Nombre_negocio varchar(100),

sub_negocio int,

idPC int,

foreign key (sub_negocio) references Subtipo(id_ST),

foreign key (idPC) references Jerarquia(id_PC)

);


create table Subtipo(

id_ST int primary key,

Nombre_subtipo varchar(100));


create table Jerarquia(

id_PC int primary key,

PC varchar(100)

);


create table Rentabilidad(

cod_transaccion int primary key,

num_unidades float,

valor_unidad float,

valor_fondo_cierre float,

num_invers int,

rentab_dia float,

rentab_mes float,

rentab_sem float,

rentab_año float

);