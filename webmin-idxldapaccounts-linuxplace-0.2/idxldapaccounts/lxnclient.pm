#!/usr/bin/perl 
#
# Acesso ao cmdserver linuxplace
# Sem documentação perl por enquanto
# Fique a vontade para contribuir
# Fernando Augusto Medeiros Silva  <fams@linupxlace.com.br>
# Copyright: Server Place LTDA
#
# Version $Id$
#
package lxnclient;
my $lxnCensus = 0;

use strict;
use POSIX qw(setsid);
use Net::SSH qw(sshopen2);
use Fcntl;
use IO::Select;


sub new {
        my $proto = shift;
        my $class = ref($proto) || $proto;
        my $self  = {};
        $lxnCensus++;
        $self->{USER}    = undef;
        $self->{HOST}    = undef;
        $self->{TIMEOUT} = 5;
        $self->{READER}  = \*READER;
        $self->{WRITER}  = \*WRITER;
        $self->{MSG}     = undef;
        bless ($self, $class);
        return $self;
}

sub connect{
    my $self = shift;
    $self->{USER} = shift;
    $self->{HOST} = shift;
    if ( not defined $self->{USER} || not defined $self->{HOST}) {
        return 0;
    }
    sshopen2($self->{USER}."\@".$self->{HOST}, $self->{READER}, $self->{WRITER}) ||  return 0;
}

##############
# remoteexec
# 
# executa procedimento remoto
# recebe o usuário remoto, o host remot, o comando a ser executado,
# referencia para a mensagem
# o retorno pode ser:
# 0  : nem um nem outro, erro interno de processamento
# 1  : funcionou
# 2  : problema
#
#
sub exec{
    my $self = shift;
    my $cmd = shift;
    $|=1;

    my $return = $self->waitfor("^cmd >");
    if ($return){
        $self->ipcchomp();
        local *WRITER =  $self->{WRITER}; 
        print WRITER "$cmd\n";
    }
    else{
        #referencia
        $self->{MSG} = "Nao recebi prompt ";
        return 0;
    }

    #Espera um erro aceitavel
    $return = $self->waitfor( "^(OK|ERR).*\n" );

    #limpa o buffer de leitura
    $self->ipcchomp();

    if ($return){
        my ( $status , @msg ) = split ( /:/ , $return );
        my $msg = join ( ":" , @msg );
        if( $status =~ 'OK') {
            $self->{MSG} = $msg;
            return 1;
        }
        else{
            $self->{MSG} = $msg;
            return 2;
        }
    }
    else{
        $self->{MSG} = "Resposta invalida do servidor ao executar $cmd";
        return 0;
    }
}
        

#################
# 
# Functions
#
# nonblock($socket) puts socket into nonblocking mode
sub nonblock {
    my $socket = shift;
    my $flags;
    
    $flags = fcntl($socket, F_GETFL, 0)
            or die "Can't get flags for socket: $!\n";
    fcntl($socket, F_SETFL, $flags | O_NONBLOCK)
            or die "Can't make socket nonblocking: $!\n";
}

sub waitfor{
    my ($self,$pattern,$timeout) = @_;
    my $found = 0;
    my $buff = "";
    my $read = "";
    my @fhs;
    if(!defined $timeout){
        $timeout = $self->{TIMEOUT};
    }
    local *READER = $self->{READER};

    #Ok let's try nonblok I/O
    nonblock( *READER );
    my  $select = IO::Select->new( *READER );

    while ( @fhs = $select->can_read($timeout)) {
        foreach my $handle ( @fhs ){
            my $bytes = sysread( $handle, $buff , 4096 );
            if ( ! $bytes  ){  
                return 0;
            }
            else{
                $read .= $buff;
                if( defined $pattern && $read =~ /($pattern)/ ){
                    return $1;
                } 
            }
        }    
    }
    return $found ;
}

sub ipcchomp{
    my $self = shift;
    $self->waitfor(undef,2);
}
sub DESTROY {
    my $self = shift;
    $lxnCensus--;
    close $self->{READER};
    close $self->{WRITER};
}


1;
